class AIChatHandler:
    def __init__(self):
        self.templates = {
            'morning': [
                "Pagi bro! Jangan lupa target hari ini: {goals}",
                "Rise and grind! Bismillah hari ini: {tasks}",
                "Good morning! Progress kemarin: {progress}"
            ],
            'study': [
                "Waktunya belajar nih! Focus points: {topics}",
                "Break dulu, udah {time} menit belajar",
                "Progress bagus! Udah {completed} soal"
            ],
            'motivation': [
                "Semangat bro! Tinggal {remaining} hari ke tes BULOG",
                "Yang penting konsisten! Udah {streak} hari streak",
                "Bisa kok, pelan-pelan aja. Progress: {progress}%"
            ]
        }
