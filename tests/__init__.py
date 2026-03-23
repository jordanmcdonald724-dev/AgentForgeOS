import warnings

warnings.simplefilter("ignore", ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"httpx\..*")
warnings.filterwarnings("ignore", category=ResourceWarning, module=r"anyio\..*")
