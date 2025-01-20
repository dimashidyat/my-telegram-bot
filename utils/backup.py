import os
import json
import shutil
from datetime import datetime
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class BackupSystem:
    def __init__(self, data_dir: str = "data", backup_dir: str = "backups"):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)

    def create_backup(self) -> bool:
        """Create backup of all data files"""
        try:
            # Create timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                self.backup_dir,
                f"backup_{timestamp}"
            )
            os.makedirs(backup_path, exist_ok=True)

            # Copy all JSON files
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    src = os.path.join(self.data_dir, filename)
                    dst = os.path.join(backup_path, filename)
                    shutil.copy2(src, dst)

            logger.info(f"Backup created: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False

    def restore_backup(self, backup_name: str) -> bool:
        """Restore from specific backup"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                logger.error(f"Backup not found: {backup_path}")
                return False

            # Copy files back to data dir
            for filename in os.listdir(backup_path):
                if filename.endswith('.json'):
                    src = os.path.join(backup_path, filename)
                    dst = os.path.join(self.data_dir, filename)
                    shutil.copy2(src, dst)

            logger.info(f"Restored from backup: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False

    def list_backups(self) -> List[Dict[str, str]]:
        """List all available backups"""
        try:
            backups = []
            for dirname in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, dirname)
                if os.path.isdir(backup_path):
                    backup_info = {
                        'name': dirname,
                        'date': datetime.fromtimestamp(
                            os.path.getctime(backup_path)
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        'size': self.get_dir_size(backup_path)
                    }
                    backups.append(backup_info)

            return sorted(backups, key=lambda x: x['date'], reverse=True)

        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []

    def cleanup_old_backups(self, keep_count: int = 5):
        """Remove old backups keeping only recent ones"""
        try:
            backups = self.list_backups()
            
            # Remove old backups
            for backup in backups[keep_count:]:
                backup_path = os.path.join(self.backup_dir, backup['name'])
                shutil.rmtree(backup_path)
                logger.info(f"Removed old backup: {backup['name']}")

        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")

    def get_dir_size(self, directory: str) -> str:
        """Get directory size in human readable format"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        # Convert to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0

        return f"{total_size:.1f} TB"

    def export_data(self, export_path: str) -> bool:
        """Export all data to single JSON file"""
        try:
            # Collect all data
            export_data = {}
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    name = filename.replace('.json', '')
                    filepath = os.path.join(self.data_dir, filename)
                    with open(filepath, 'r') as f:
                        export_data[name] = json.load(f)

            # Save to export file
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Data exported to: {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def import_data(self, import_path: str) -> bool:
        """Import data from exported JSON file"""
        try:
            # Create backup first
            self.create_backup()

            # Load import file
            with open(import_path, 'r') as f:
                import_data = json.load(f)

            # Save each section
            for name, data in import_data.items():
                filepath = os.path.join(self.data_dir, f"{name}.json")
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)

            logger.info(f"Data imported from: {import_path}")
            return True

        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return False
