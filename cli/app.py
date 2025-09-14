"""
Capfit CLI 애플리케이션
"""

from shared.cli import CapfitCLI

def main():
    """CLI 애플리케이션 진입점"""
    cli = CapfitCLI()
    app = cli.get_app()
    app()

if __name__ == "__main__":
    main()
