import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Formatter:
    def __init__(self):
        self.hari = {
            0: 'Senin',
            1: 'Selasa',
            2: 'Rabu',
            3: 'Kamis',
            4: 'Jumat',
            5: 'Sabtu',
            6: 'Minggu'
        }

    def format_pempek_report(self, data: Dict[str, Any]) -> str:
        """Format pempek daily report"""
        try:
            now = datetime.now()
            
            # Format header
            report = (
                f"*Laporan {self.hari[now.weekday()]} "
                f"{now.strftime('%d %B %Y')}*:\n\n"
            )

            # 1. Pengeluaran
            report += "1. *Pengeluaran*\n"
            total_pengeluaran = 0
            for idx, (item, amount) in enumerate(data.get('pengeluaran', {}).items()):
                report += f"{chr(97+idx)}. {item} : Rp. {amount:,},-\n"
                total_pengeluaran += amount
            report += "------------------------------- +\n"
            report += f"Rp. {total_pengeluaran:,},-\n\n"

            # 2. Sisa pempek
            report += "2. *Sisa*\n"
            kecil = data.get('sisa', {}).get('kecil', 0)
            gede = data.get('sisa', {}).get('gede', 0)
            
            kecil_value = kecil * 2500
            gede_value = gede * 12000
            total_sisa = kecil_value + gede_value
            
            report += f"a. Kecil: {kecil} biji -> {kecil} x2.500 = {kecil_value:,}\n"
            report += f"b. Gede: {gede} biji -> {gede} x12.000 = {gede_value:,}\n"
            report += "Total ---------------------+\n"
            report += f"Rp. {total_sisa:,},-\n\n"

            # 3. Setoran
            report += "3. *Setoran*\n"
            qris = data.get('setoran', {}).get('qris', 0)
            cash = data.get('setoran', {}).get('cash', 0)
            total_setoran = qris + cash
            
            report += f"qris : {qris:,}\n"
            report += f"Cash : {cash:,}\n"
            report += f"total : {total_setoran:,}\n\n"

            # 4. Sisa plastik
            report += "4. *Sisa plastik*\n"
            plastik = data.get('plastik', {})
            sizes = {'1/4': 'a', '1/2': 'b', '1': 'c', 'kantong': 'd'}
            
            for size, prefix in sizes.items():
                if size in plastik:
                    baik = plastik[size].get('baik', 0)
                    rusak = plastik[size].get('rusak', 0)
                    report += f"{prefix}. {size} : Br: {baik} ;Bs: {rusak}\n"

            # Minyak status
            report += "*Minyak*\n"
            report += plastik.get('minyak', 'tidak ada data')

            return report

        except Exception as e:
            logger.error(f"Error formatting pempek report: {e}")
            return "Error generating report"

    def format_currency(self, amount: int) -> str:
        """Format currency with thousand separator"""
        try:
            return f"Rp{amount:,},-"
        except Exception as e:
            logger.error(f"Error formatting currency: {e}")
            return str(amount)

    def format_study_progress(self, data: Dict[str, Any]) -> str:
        """Format study progress report"""
        try:
            categories = {
                'TWK': {'target': 20, 'name': 'Wawasan Kebangsaan'},
                'TIU': {'target': 15, 'name': 'Intelegensi Umum'},
                'TKP': {'target': 10, 'name': 'Karakteristik Pribadi'}
            }
            
            report = "*📊 PROGRESS BELAJAR BULOG*\n\n"
            
            # Add progress per category
            for code, info in categories.items():
                done = data.get(code, 0)
                target = info['target']
                percentage = (done / target) * 100
                
                report += f"*{code} - {info['name']}*\n"
                report += f"• Progress: {done}/{target} soal\n"
                report += f"• Complete: {percentage:.1f}%\n\n"

            # Add study time
            study_time = data.get('study_time', 0)
            report += f"⏱️ Total waktu: {study_time} menit\n"
            report += f"🔥 Streak: {data.get('streak', 0)} hari\n"
            
            return report

        except Exception as e:
            logger.error(f"Error formatting study progress: {e}")
            return "Error generating progress report"

    def format_health_stats(self, data: Dict[str, Any]) -> str:
        """Format health statistics"""
        try:
            report = "*💪 HEALTH STATISTICS*\n\n"
            
            # Workout stats
            report += "*Workout Progress:*\n"
            report += f"• Today: {data.get('workout', 0)}/30 menit\n"
            report += f"• Week: {data.get('weekly_workout', 0)}/180 menit\n"
            report += f"• Streak: {data.get('workout_streak', 0)} hari\n\n"
            
            # Sleep stats
            report += "*Sleep Track:*\n"
            report += f"• Average: {data.get('avg_sleep', 0)} jam\n"
            report += f"• Quality: {data.get('sleep_quality', 'N/A')}\n"
            report += f"• Streak: {data.get('sleep_streak', 0)} hari\n\n"
            
            # Other stats
            report += "*Other Stats:*\n"
            report += f"• Water: {data.get('water', 0)}/2 liter\n"
            report += f"• Weight: {data.get('weight', 'N/A')} kg\n"
            
            return report

        except Exception as e:
            logger.error(f"Error formatting health stats: {e}")
            return "Error generating health report" 
