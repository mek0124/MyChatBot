#!/usr/bin/env python3
"""
Build script for MyChatBot that creates standalone executables for all platforms.
Organizes outputs into platform-specific subdirectories.
"""
import os
import sys
import platform
import subprocess
import shutil
import tarfile
from pathlib import Path
from abc import ABC, abstractmethod

class PlatformBuilder(ABC):
    """Abstract base class for platform-specific builders"""
    
    def __init__(self, platform_name):
        self.platform_name = platform_name
        self.dist_dir = Path('dist') / platform_name
        self.pyinstaller_cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',
            '--name=MyChatBot',
            '--add-data=frontend/assets/app-icon.jpeg:frontend/assets',
            '--add-data=frontend/assets/icon.ico:frontend/assets',
            '--hidden-import=PySide6.QtCore',
            '--hidden-import=PySide6.QtGui',
            '--hidden-import=PySide6.QtWidgets',
            '--hidden-import=markdown',
            '--hidden-import=mistralai',
            '--hidden-import=python_dotenv',
            'main.py'
        ]
    
    def clean_build_dirs(self):
        """Clean previous build directories"""
        for folder in ['build']:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        
        # Clean only this platform's dist directory
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
    
    def run_pyinstaller(self):
        """Run PyInstaller with platform-specific commands"""
        self._modify_pyinstaller_cmd()
        # Set the distpath to our platform-specific directory
        self.pyinstaller_cmd.extend(['--distpath', str(self.dist_dir)])
        subprocess.run(self.pyinstaller_cmd, check=True)
    
    @abstractmethod
    def _modify_pyinstaller_cmd(self):
        """Platform-specific modifications to PyInstaller command"""
        pass
    
    @abstractmethod
    def package(self):
        """Platform-specific packaging of the build output"""
        pass

class LinuxBuilder(PlatformBuilder):
    """Builder for Linux platform"""
    
    def __init__(self):
        super().__init__('linux')
    
    def _modify_pyinstaller_cmd(self):
        self.pyinstaller_cmd.extend(['--onefile'])
    
    def package(self):
        """Package Linux executable into a tar.gz"""
        bin_path = self.dist_dir / 'MyChatBot'
        if bin_path.exists():
            # Create platform-specific output directory
            output_dir = Path('dist') / 'packaged'
            output_dir.mkdir(exist_ok=True)
            
            # Create a simple run script
            run_script_path = self.dist_dir / 'run_MyChatBot.sh'
            with open(run_script_path, 'w') as f:
                f.write("#!/bin/sh\n")
                f.write(f'DIR="$( cd "$( dirname "$0" )" && pwd )"\n')
                f.write('"$DIR/MyChatBot" "$@"\n')
            os.chmod(run_script_path, 0o755)
            
            # Create tar.gz in the packaged directory
            with tarfile.open(output_dir / 'MyChatBot-Linux.tar.gz', 'w:gz') as tar:
                tar.add(bin_path, arcname='MyChatBot')
                tar.add(run_script_path, arcname='run_MyChatBot.sh')
            print(f"Created {output_dir/'MyChatBot-Linux.tar.gz'}")

class MacBuilder(PlatformBuilder):
    """Builder for macOS platform"""
    
    def __init__(self):
        super().__init__('mac')
    
    def _modify_pyinstaller_cmd(self):
        self.pyinstaller_cmd.extend([
            '--osx-bundle-identifier=com.yourcompany.mychatbot',
            '--windowed'  # Proper .app bundle
        ])
    
    def package(self):
        """Package Mac .app into a zip"""
        app_path = self.dist_dir / 'MyChatBot.app'
        if app_path.exists():
            # Create platform-specific output directory
            output_dir = Path('dist') / 'packaged'
            output_dir.mkdir(exist_ok=True)
            
            # Create a simple command script
            command_script_path = self.dist_dir / 'Run_MyChatBot.command'
            with open(command_script_path, 'w') as f:
                f.write("#!/bin/sh\n")
                f.write(f'open "{app_path}"\n')
            os.chmod(command_script_path, 0o755)
            
            # Zip both the app and the command script
            shutil.make_archive(
                str(output_dir / 'MyChatBot-macOS'), 
                'zip', 
                str(self.dist_dir))
            print(f"Created {output_dir/'MyChatBot-macOS.zip'}")

class WindowsBuilder(PlatformBuilder):
    """Builder for Windows platform"""
    
    def __init__(self):
        super().__init__('windows')
    
    def _modify_pyinstaller_cmd(self):
        self.pyinstaller_cmd.extend(['--onefile', '--noconsole'])
        # Windows needs semicolons in add-data
        for i, arg in enumerate(self.pyinstaller_cmd):
            if arg.startswith('--add-data='):
                self.pyinstaller_cmd[i] = arg.replace(':', ';')
    
    def package(self):
        """Package Windows .exe into a zip"""
        exe_path = self.dist_dir / 'MyChatBot.exe'
        if exe_path.exists():
            # Create platform-specific output directory
            output_dir = Path('dist') / 'packaged'
            output_dir.mkdir(exist_ok=True)
            
            shutil.make_archive(
                str(output_dir / 'MyChatBot-Windows'), 
                'zip', 
                str(self.dist_dir))
            print(f"Created {output_dir/'MyChatBot-Windows.zip'}")

class BuildManager:
    """Main build manager that handles the build process"""
    
    def __init__(self):
        self.current_system = platform.system()
        print(f"Building for current platform: {self.current_system}")
    
    def build(self):
        """Execute the build process for the current platform"""
        # Ensure dist directory exists
        Path('dist').mkdir(exist_ok=True)
        
        if self.current_system == "Linux":
            # On Linux, build both Linux and Mac versions
            self._build_platforms([LinuxBuilder(), MacBuilder()])
        elif self.current_system == "Windows":
            # On Windows, build only Windows version
            self._build_platforms([WindowsBuilder()])
        else:  # Darwin (macOS)
            # On Mac, build only Mac version
            self._build_platforms([MacBuilder()])
        
        self._warn_about_other_platforms()
    
    def _build_platforms(self, builders):
        """Build for multiple platforms"""
        for builder in builders:
            print(f"\nBuilding for {builder.platform_name}...")
            builder.clean_build_dirs()
            builder.run_pyinstaller()
            builder.package()
    
    def _warn_about_other_platforms(self):
        """Warn about platforms that need to be built on their native systems"""
        other_platforms = {
            "Windows": self.current_system == "Windows",
            "macOS": self.current_system == "Darwin",
            "Linux": self.current_system == "Linux"
        }
        
        print("\nNote about cross-platform building:")
        for platform_name, is_current in other_platforms.items():
            if not is_current:
                print(f"- {platform_name} builds must be created on a {platform_name} system")

if __name__ == "__main__":
    try:
        import tarfile
    except ImportError:
        print("Error: tarfile module not found")
        sys.exit(1)
    
    BuildManager().build()