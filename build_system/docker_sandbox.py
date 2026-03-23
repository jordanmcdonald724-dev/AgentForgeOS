"""
Docker Build Sandbox System

Provides secure, isolated build environments for AgentForgeOS projects
using Docker containers with proper resource limits and security controls.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import subprocess
import shutil

logger = logging.getLogger(__name__)


@dataclass
class SandboxConfig:
    """Configuration for Docker sandbox environment"""
    image: str = "agentforge/build-sandbox:latest"
    memory_limit: str = "2g"
    cpu_limit: str = "1.0"
    timeout: int = 300  # 5 minutes
    network_mode: str = "none"  # Isolated network
    read_only: bool = False
    temp_dir: Optional[str] = None
    environment: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {}


@dataclass
class BuildRequest:
    """Build request for sandbox execution"""
    project_id: str
    command: str
    working_dir: str
    files: Dict[str, str] = None  # filename -> content
    environment: Dict[str, str] = None
    requirements: List[str] = None  # pip packages, etc.
    
    def __post_init__(self):
        if self.files is None:
            self.files = {}
        if self.environment is None:
            self.environment = {}
        if self.requirements is None:
            self.requirements = []


@dataclass
class BuildResult:
    """Result from sandboxed build execution"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    container_id: str
    artifacts: Dict[str, str] = None  # filename -> content
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = {}


class DockerSandbox:
    """
    Docker-based build sandbox for secure code execution.
    
    Provides:
    - Isolated build environments
    - Resource limits (CPU, memory, time)
    - File system isolation
    - Network isolation
    - Artifact extraction
    - Security controls
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.temp_base = Path(self.config.temp_dir or tempfile.gettempdir()) / "agentforge_sandbox"
        self.temp_base.mkdir(parents=True, exist_ok=True)
        
        # Verify Docker availability
        self._verify_docker()
        
        logger.info(f"DockerSandbox initialized with image: {self.config.image}")
    
    def _verify_docker(self) -> None:
        """Verify Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                logger.warning("Docker not available - sandbox features will be limited")
                return
            
            # Check if Docker daemon is running
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                logger.warning("Docker daemon not running - sandbox features will be limited")
                return
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Docker verification failed: {e} - sandbox features will be limited")
    
    async def execute_build(self, request: BuildRequest) -> BuildResult:
        """
        Execute a build request in a Docker sandbox.
        
        Args:
            request: Build request with command and files
            
        Returns:
            BuildResult with execution results
        """
        container_id = f"agentforge_build_{uuid.uuid4().hex[:12]}"
        temp_dir = self.temp_base / container_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Prepare build environment
            await self._prepare_build_environment(temp_dir, request)
            
            # Create and run container
            docker_run_cmd = self._build_docker_command(container_id, temp_dir, request)
            
            logger.info(f"Starting container {container_id} for project {request.project_id}")
            
            # Execute Docker command
            process = await asyncio.create_subprocess_exec(
                *docker_run_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(temp_dir)
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.config.timeout
                )
                exit_code = process.returncode
            except asyncio.TimeoutError:
                # Kill container on timeout
                await self._cleanup_container(container_id)
                return BuildResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Build timed out after {self.config.timeout} seconds",
                    execution_time=self.config.timeout,
                    container_id=container_id,
                    error="TIMEOUT"
                )
            
            # Calculate execution time
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Extract artifacts
            artifacts = await self._extract_artifacts(container_id, temp_dir)
            
            # Determine success
            success = exit_code == 0
            
            result = BuildResult(
                success=success,
                exit_code=exit_code,
                stdout=stdout.decode('utf-8', errors='replace'),
                stderr=stderr.decode('utf-8', errors='replace'),
                execution_time=execution_time,
                container_id=container_id,
                artifacts=artifacts,
                error=None if success else f"Build failed with exit code {exit_code}"
            )
            
            logger.info(f"Container {container_id} completed: success={success}, time={execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Build execution failed for {container_id}: {e}")
            return BuildResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=(datetime.now(timezone.utc) - start_time).total_seconds(),
                container_id=container_id,
                error=str(e)
            )
        finally:
            # Cleanup container and temp files
            await self._cleanup_container(container_id)
            await self._cleanup_temp_files(temp_dir)
    
    async def _prepare_build_environment(self, temp_dir: Path, request: BuildRequest) -> None:
        """Prepare the build environment with files and dependencies."""
        # Write project files
        for filename, content in request.files.items():
            file_path = temp_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
        
        # Create requirements.txt if needed
        if request.requirements:
            req_file = temp_dir / "requirements.txt"
            req_file.write_text('\n'.join(request.requirements), encoding='utf-8')
        
        # Create build script
        build_script = self._generate_build_script(request)
        script_path = temp_dir / "build.sh"
        script_path.write_text(build_script, encoding='utf-8')
        script_path.chmod(0o755)  # Make executable
        
        # Create environment file
        if request.environment:
            env_file = temp_dir / ".env"
            env_content = '\n'.join([f"{k}={v}" for k, v in request.environment.items()])
            env_file.write_text(env_content, encoding='utf-8')
    
    def _generate_build_script(self, request: BuildRequest) -> str:
        """Generate build script for the container."""
        script = f"""#!/bin/bash
set -e

echo "Starting AgentForgeOS build..."
echo "Project ID: {request.project_id}"
echo "Working directory: {request.working_dir}"
echo "Command: {request.command}"

# Create working directory
mkdir -p {request.working_dir}
cd {request.working_dir}

"""
        
        # Install requirements if any
        if request.requirements:
            script += """
# Install Python requirements
if [ -f "/workspace/requirements.txt" ]; then
    echo "Installing Python requirements..."
    pip install --no-cache-dir -r /workspace/requirements.txt
fi
"""
        
        # Add the main command
        script += f"""
echo "Executing build command..."
{request.command}

echo "Build completed successfully!"
"""
        
        return script
    
    def _build_docker_command(self, container_id: str, temp_dir: Path, request: BuildRequest) -> List[str]:
        """Build Docker command for container execution."""
        cmd = [
            "docker", "run",
            "--rm",
            "--name", container_id,
            "--memory", self.config.memory_limit,
            "--cpus", self.config.cpu_limit,
            "--network", self.config.network_mode,
        ]
        
        # Add read-only flag if specified
        if self.config.read_only:
            cmd.append("--read-only")
        
        # Mount workspace directory
        workspace_mount = f"{temp_dir}:/workspace"
        cmd.extend(["-v", workspace_mount])
        
        # Add environment variables
        for key, value in self.config.environment.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Add request-specific environment
        for key, value in request.environment.items():
            cmd.extend(["-e", f"{key}={value}"])
        
        # Add image and command
        cmd.extend([
            self.config.image,
            "/bin/bash", "/workspace/build.sh"
        ])
        
        return cmd
    
    async def _extract_artifacts(self, container_id: str, temp_dir: Path) -> Dict[str, str]:
        """Extract build artifacts from the container."""
        artifacts = {}
        
        try:
            # List files in working directory
            ls_cmd = ["docker", "run", "--rm", "-v", f"{temp_dir}:/workspace", self.config.image, "ls", "-R", "/workspace"]
            
            process = await asyncio.create_subprocess_exec(
                *ls_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse file listing and extract relevant files
                file_list = stdout.decode('utf-8').strip().split('\n')
                
                for file_path in file_list:
                    if file_path and not file_path.endswith('/') and not file_path.startswith('./'):
                        full_path = temp_dir / file_path
                        if full_path.is_file() and full_path.stat().st_size < 1024 * 1024:  # < 1MB
                            try:
                                content = full_path.read_text(encoding='utf-8')
                                artifacts[file_path] = content
                            except Exception as e:
                                logger.warning(f"Failed to read artifact {file_path}: {e}")
            
        except Exception as e:
            logger.warning(f"Failed to extract artifacts from {container_id}: {e}")
        
        return artifacts
    
    async def _cleanup_container(self, container_id: str) -> None:
        """Clean up Docker container."""
        try:
            # Stop and remove container
            await asyncio.create_subprocess_exec(
                "docker", "stop", container_id,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            await asyncio.create_subprocess_exec(
                "docker", "rm", container_id,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
        except Exception as e:
            logger.warning(f"Failed to cleanup container {container_id}: {e}")
    
    async def _cleanup_temp_files(self, temp_dir: Path) -> None:
        """Clean up temporary files."""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files {temp_dir}: {e}")
    
    async def get_sandbox_info(self) -> Dict[str, Any]:
        """Get information about the sandbox system."""
        try:
            # Get Docker info
            result = await asyncio.create_subprocess_exec(
                "docker", "info", "--format", "{{json .}}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                docker_info = json.loads(stdout.decode('utf-8'))
            else:
                docker_info = {"error": stderr.decode('utf-8')}
            
            # Check if sandbox image exists
            image_result = await asyncio.create_subprocess_exec(
                "docker", "images", "-q", self.config.image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            image_stdout, image_stderr = await image_result.communicate()
            image_exists = bool(image_stdout.strip())
            
            return {
                "docker_available": True,
                "sandbox_image": self.config.image,
                "image_exists": image_exists,
                "temp_directory": str(self.temp_base),
                "config": asdict(self.config),
                "docker_info": docker_info
            }
            
        except Exception as e:
            return {
                "docker_available": False,
                "error": str(e),
                "config": asdict(self.config)
            }
    
    async def build_sandbox_image(self) -> bool:
        """Build the sandbox Docker image if it doesn't exist."""
        try:
            # Check if image already exists
            info = await self.get_sandbox_info()
            if info.get("image_exists", False):
                logger.info(f"Sandbox image {self.config.image} already exists")
                return True
            
            # Create Dockerfile
            dockerfile = self._generate_dockerfile()
            dockerfile_path = self.temp_base / "Dockerfile"
            dockerfile_path.write_text(dockerfile, encoding='utf-8')
            
            logger.info(f"Building sandbox image {self.config.image}...")
            
            # Build Docker image
            process = await asyncio.create_subprocess_exec(
                "docker", "build",
                "-t", self.config.image,
                str(self.temp_base),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Successfully built sandbox image {self.config.image}")
                return True
            else:
                logger.error(f"Failed to build sandbox image: {stderr.decode('utf-8')}")
                return False
                
        except Exception as e:
            logger.error(f"Error building sandbox image: {e}")
            return False
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile for the sandbox image."""
        return """
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    git \\
    curl \\
    wget \\
    unzip \\
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Create non-root user for security
RUN useradd -m -u 1000 builder && chown -R builder:builder /workspace
USER builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install common Python packages
RUN pip install --no-cache-dir \\
    setuptools \\
    wheel \\
    pip \\
    poetry \\
    nodejs \\
    npm

# Create build script directory
RUN mkdir -p /tmp/build

# Default command
CMD ["/bin/bash"]
""".strip()


# Global sandbox instance
try:
    docker_sandbox = DockerSandbox()
except Exception as e:
    logger.warning(f"Failed to initialize Docker sandbox: {e}")
    docker_sandbox = None
