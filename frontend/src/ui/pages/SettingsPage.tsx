/**
 * Settings Page Component
 * 
 * Comprehensive settings management interface for AgentForgeOS V2.
 * Provides configuration for AI models, databases, game engines,
 * sandboxing, and system preferences.
 */

import React, { useState, useEffect } from 'react';

// Simple UI components (replace with actual UI library components)
const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`border rounded-lg shadow-sm ${className}`}>{children}</div>
);

const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`p-4 border-b ${className}`}>{children}</div>
);

const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`p-4 ${className}`}>{children}</div>
);

const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold ${className}`}>{children}</h3>
);

const Button: React.FC<{ 
  children: React.ReactNode; 
  onClick?: () => void; 
  variant?: string; 
  className?: string;
  disabled?: boolean;
}> = ({ children, onClick, variant = 'default', className = '', disabled = false }) => {
  const baseClasses = 'px-4 py-2 rounded font-medium transition-colors';
  const variantClasses = {
    default: 'bg-blue-500 text-white hover:bg-blue-600',
    outline: 'border border-gray-300 text-gray-700 hover:bg-gray-50',
    destructive: 'bg-red-500 text-white hover:bg-red-600',
  };
  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant as keyof typeof variantClasses]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

const Input: React.FC<{ 
  type?: string; 
  value?: string | number; 
  onChange?: (value: string) => void; 
  placeholder?: string;
  className?: string;
  min?: string;
  max?: string;
  step?: string;
}> = ({ type = 'text', value = '', onChange, placeholder, className = '', min, max, step }) => (
  <input 
    type={type}
    value={value}
    onChange={(e) => onChange?.(e.target.value)}
    placeholder={placeholder}
    min={min}
    max={max}
    step={step}
    className={`w-full px-3 py-2 border rounded-md ${className}`}
  />
);

const Select: React.FC<{ 
  value?: string; 
  onChange?: (value: string) => void; 
  children: React.ReactNode;
  className?: string;
}> = ({ value = '', onChange, children, className = '' }) => (
  <select 
    value={value}
    onChange={(e) => onChange?.(e.target.value)}
    className={`w-full px-3 py-2 border rounded-md ${className}`}
  >
    {children}
  </select>
);

const Switch: React.FC<{ 
  checked?: boolean; 
  onChange?: (checked: boolean) => void; 
  label?: string;
}> = ({ checked = false, onChange, label }) => (
  <label className="flex items-center space-x-2">
    <input 
      type="checkbox" 
      checked={checked}
      onChange={(e) => onChange?.(e.target.checked)}
      className="rounded"
    />
    <span>{label}</span>
  </label>
);

interface SettingsState {
  // AI Model Settings
  falApiKey: string;
  openaiApiKey: string;
  defaultModelProvider: string;
  modelTemperature: number;
  maxTokens: number;
  
  // Database Settings
  mongoUrl: string;
  dbName: string;
  neo4jUri: string;
  neo4jUser: string;
  neo4jPassword: string;
  qdrantHost: string;
  qdrantPort: string;
  
  // Game Engine Settings
  unityEditorPath: string;
  unrealEditorPath: string;
  defaultGameEngine: string;
  
  // Sandbox Settings
  dockerEnabled: boolean;
  sandboxImage: string;
  memoryLimit: string;
  cpuLimit: string;
  timeout: number;
  
  // System Settings
  logLevel: string;
  maxConcurrentTasks: number;
  enableRealtimeUpdates: boolean;
  enableTelemetry: boolean;
}

const defaultSettings: SettingsState = {
  // AI Model Settings
  falApiKey: '',
  openaiApiKey: '',
  defaultModelProvider: 'fal',
  modelTemperature: 0.7,
  maxTokens: 4096,
  
  // Database Settings
  mongoUrl: 'mongodb://localhost:27017',
  dbName: 'agentforge_v2',
  neo4jUri: 'bolt://localhost:7687',
  neo4jUser: 'neo4j',
  neo4jPassword: '',
  qdrantHost: 'localhost',
  qdrantPort: '6333',
  
  // Game Engine Settings
  unityEditorPath: 'C:/Program Files/Unity/Editor/Unity.exe',
  unrealEditorPath: 'C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/Win64/UnrealEditor.exe',
  defaultGameEngine: 'unity',
  
  // Sandbox Settings
  dockerEnabled: true,
  sandboxImage: 'agentforge/build-sandbox:latest',
  memoryLimit: '2g',
  cpuLimit: '1.0',
  timeout: 300,
  
  // System Settings
  logLevel: 'INFO',
  maxConcurrentTasks: 5,
  enableRealtimeUpdates: true,
  enableTelemetry: false,
};

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SettingsState>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('ai-models');
  const [testResults, setTestResults] = useState<Record<string, boolean>>({});

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would load from the backend API
      const response = await fetch('/api/settings');
      if (response.ok) {
        const loadedSettings = await response.json();
        setSettings({ ...defaultSettings, ...loadedSettings });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      // In a real implementation, this would save to the backend API
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      
      if (response.ok) {
        // Show success message
        alert('Settings saved successfully!');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      alert('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const testConnection = async (service: string) => {
    try {
      const response = await fetch(`/api/settings/test/${service}`);
      const result = await response.json();
      setTestResults(prev => ({ ...prev, [service]: result.success }));
    } catch (error) {
      setTestResults(prev => ({ ...prev, [service]: false }));
    }
  };

  const updateSetting = (category: keyof SettingsState, value: any) => {
    setSettings(prev => ({ ...prev, [category]: value }));
  };

  const tabs = [
    { id: 'ai-models', label: 'AI Models', icon: '🤖' },
    { id: 'databases', label: 'Databases', icon: '🗄️' },
    { id: 'game-engines', label: 'Game Engines', icon: '🎮' },
    { id: 'sandbox', label: 'Sandbox', icon: '📦' },
    { id: 'system', label: 'System', icon: '⚙️' },
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-600">Configure AgentForgeOS V2 system settings and preferences</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 border-b">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab.id
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'ai-models' && (
          <Card>
            <CardHeader>
              <CardTitle>AI Model Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">fal.ai API Key</label>
                  <Input
                    type="password"
                    value={settings.falApiKey}
                    onChange={(value) => updateSetting('falApiKey', value)}
                    placeholder="Enter your fal.ai API key"
                  />
                  <Button 
                    variant="outline" 
                    className="mt-2"
                    onClick={() => testConnection('fal')}
                  >
                    Test Connection
                  </Button>
                  {testResults.fal !== undefined && (
                    <span className={`ml-2 ${testResults.fal ? 'text-green-600' : 'text-red-600'}`}>
                      {testResults.fal ? '✅ Connected' : '❌ Failed'}
                    </span>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">OpenAI API Key</label>
                  <Input
                    type="password"
                    value={settings.openaiApiKey}
                    onChange={(value) => updateSetting('openaiApiKey', value)}
                    placeholder="Enter your OpenAI API key"
                  />
                  <Button 
                    variant="outline" 
                    className="mt-2"
                    onClick={() => testConnection('openai')}
                  >
                    Test Connection
                  </Button>
                  {testResults.openai !== undefined && (
                    <span className={`ml-2 ${testResults.openai ? 'text-green-600' : 'text-red-600'}`}>
                      {testResults.openai ? '✅ Connected' : '❌ Failed'}
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Default Provider</label>
                  <Select
                    value={settings.defaultModelProvider}
                    onChange={(value) => updateSetting('defaultModelProvider', value)}
                  >
                    <option value="fal">fal.ai</option>
                    <option value="openai">OpenAI</option>
                    <option value="local">Local Models</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Model Temperature</label>
                  <Input
                    type="number"
                    value={settings.modelTemperature}
                    onChange={(value) => updateSetting('modelTemperature', parseFloat(value))}
                    min="0"
                    max="2"
                    step="0.1"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Max Tokens</label>
                <Input
                  type="number"
                  value={settings.maxTokens}
                  onChange={(value) => updateSetting('maxTokens', parseInt(value))}
                  min="1"
                  max="32000"
                />
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'databases' && (
          <Card>
            <CardHeader>
              <CardTitle>Database Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">MongoDB URL</label>
                <Input
                  value={settings.mongoUrl}
                  onChange={(value) => updateSetting('mongoUrl', value)}
                  placeholder="mongodb://localhost:27017"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Database Name</label>
                  <Input
                    value={settings.dbName}
                    onChange={(value) => updateSetting('dbName', value)}
                    placeholder="agentforge_v2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Neo4j URI</label>
                  <Input
                    value={settings.neo4jUri}
                    onChange={(value) => updateSetting('neo4jUri', value)}
                    placeholder="bolt://localhost:7687"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Neo4j User</label>
                  <Input
                    value={settings.neo4jUser}
                    onChange={(value) => updateSetting('neo4jUser', value)}
                    placeholder="neo4j"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Neo4j Password</label>
                  <Input
                    type="password"
                    value={settings.neo4jPassword}
                    onChange={(value) => updateSetting('neo4jPassword', value)}
                    placeholder="Enter Neo4j password"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Qdrant Host</label>
                  <Input
                    value={settings.qdrantHost}
                    onChange={(value) => updateSetting('qdrantHost', value)}
                    placeholder="localhost"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Qdrant Port</label>
                  <Input
                    value={settings.qdrantPort}
                    onChange={(value) => updateSetting('qdrantPort', value)}
                    placeholder="6333"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'game-engines' && (
          <Card>
            <CardHeader>
              <CardTitle>Game Engine Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Default Game Engine</label>
                <Select
                  value={settings.defaultGameEngine}
                  onChange={(value) => updateSetting('defaultGameEngine', value)}
                >
                  <option value="unity">Unity</option>
                  <option value="unreal">Unreal Engine</option>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Unity Editor Path</label>
                <Input
                  value={settings.unityEditorPath}
                  onChange={(value) => updateSetting('unityEditorPath', value)}
                  placeholder="C:/Program Files/Unity/Editor/Unity.exe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Unreal Editor Path</label>
                <Input
                  value={settings.unrealEditorPath}
                  onChange={(value) => updateSetting('unrealEditorPath', value)}
                  placeholder="C:/Program Files/Epic Games/UE_5.3/Engine/Binaries/Win64/UnrealEditor.exe"
                />
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'sandbox' && (
          <Card>
            <CardHeader>
              <CardTitle>Docker Sandbox Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Switch
                  checked={settings.dockerEnabled}
                  onChange={(checked) => updateSetting('dockerEnabled', checked)}
                  label="Enable Docker Sandbox"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Sandbox Image</label>
                <Input
                  value={settings.sandboxImage}
                  onChange={(value) => updateSetting('sandboxImage', value)}
                  placeholder="agentforge/build-sandbox:latest"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Memory Limit</label>
                  <Input
                    value={settings.memoryLimit}
                    onChange={(value) => updateSetting('memoryLimit', value)}
                    placeholder="2g"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">CPU Limit</label>
                  <Input
                    value={settings.cpuLimit}
                    onChange={(value) => updateSetting('cpuLimit', value)}
                    placeholder="1.0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Timeout (seconds)</label>
                <Input
                  type="number"
                  value={settings.timeout}
                  onChange={(value) => updateSetting('timeout', parseInt(value))}
                  min="30"
                  max="3600"
                />
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'system' && (
          <Card>
            <CardHeader>
              <CardTitle>System Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Log Level</label>
                  <Select
                    value={settings.logLevel}
                    onChange={(value) => updateSetting('logLevel', value)}
                  >
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Max Concurrent Tasks</label>
                  <Input
                    type="number"
                    value={settings.maxConcurrentTasks}
                    onChange={(value) => updateSetting('maxConcurrentTasks', parseInt(value))}
                    min="1"
                    max="20"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <Switch
                  checked={settings.enableRealtimeUpdates}
                  onChange={(checked) => updateSetting('enableRealtimeUpdates', checked)}
                  label="Enable Real-time Updates"
                />
                
                <Switch
                  checked={settings.enableTelemetry}
                  onChange={(checked) => updateSetting('enableTelemetry', checked)}
                  label="Enable Telemetry (Anonymous Usage Data)"
                />
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4 mt-8">
        <Button 
          variant="outline" 
          onClick={() => setSettings(defaultSettings)}
        >
          Reset to Defaults
        </Button>
        <Button 
          onClick={saveSettings}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>
    </div>
  );
};
