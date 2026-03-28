from kivy.app import App
from kivy.lang import Builder


class NetDiagApp(App):
    def build(self):
        return Builder.load_file("netdiag/ui/main.kv")

    def run_diagnostics(self):
        try:
            from netdiag.checks.orchestrator import run_all_checks
            result = run_all_checks("targets.json")
            self.root.ids.output_box.text = result
        except Exception as e:
            self.root.ids.output_box.text = f"Ошибка: {e}"