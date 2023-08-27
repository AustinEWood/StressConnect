import sys
import subprocess
import json
import csv
import logging
from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout,
                             QComboBox, QLineEdit, QPlainTextEdit, QTabWidget,
                             QPushButton, QFileDialog, QWidget, QMessageBox, QTextEdit)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# Initialize logging.
logging.basicConfig(filename='error_log.txt', level=logging.INFO)

# Thread to run the script.
class RunScriptThread(QThread):
    signal = pyqtSignal(str, str)

    def __init__(self, command):
        QThread.__init__(self)
        self.command = command

    def run(self):
        try:
            # Running PowerShell script
            result = subprocess.run(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            # Logging to error_log.txt
            if result.stdout:
                logging.info(f'STDOUT: {result.stdout}')
            if result.stderr:
                logging.error(f'STDERR: {result.stderr}')

            # Emit only the stdout and not the stderr.
            self.signal.emit(result.stdout, '')
        except Exception as e:
            # Logging to error_log.txt.
            logging.error(f'Exception: {str(e)}')
            self.signal.emit('', str(e))



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a widget for the central area.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout.
        layout = QVBoxLayout()

        # Script Selection Dropdown.
        self.script_dropdown = QComboBox()
        self.script_dropdown.addItem("Please Select A Script From The Dropdown Menu")
        self.script_dropdown.addItem("Stress Connect")
        layout.addWidget(self.script_dropdown)

        # API Key Input.
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Optional API Key")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_input)

        # Create a text edit widget for the script output.
        self.script_output = QTextEdit()
        self.script_output.setReadOnly(True)
        layout.addWidget(self.script_output)

        # Create buttons as needed (e.g., Run Script, Save Output, etc.).
        self.run_button = QPushButton('Run Script')
        layout.addWidget(self.run_button)
        self.run_button.clicked.connect(self.run_script)

        self.save_button = QPushButton('Save Output')
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_output)

        # Final Setup.
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.apply_dark_mode()

        self.setWindowIcon(QIcon("MyLogo.ico"))
        self.setWindowTitle("Stress Connect")
        self.run_button.setStyleSheet("background-color: none;") 
        self.run_button.setEnabled(False)
        self.save_button.setStyleSheet("background-color: none;")
        self.save_button.setEnabled(False)
        self.script_dropdown.currentIndexChanged.connect(self.enable_run_button)
        self.script_output.textChanged.connect(self.enable_save_button)
        self.connections = []


        # Method to handle script output.
    def handle_script_output(self, stdout, stderr):
        if stdout.strip() != "":
            self.connections = json.loads(stdout)
            formatted_output = ""
            for connection in self.connections:
                for key, value in connection.items():
                    formatted_output += f"{key}: {value}\n"
                formatted_output += '-' * 50 + '\n'
            self.script_output.setPlainText(formatted_output)

        #Method to set dark mode to say users eyes.
    def apply_dark_mode(self):
        dark_style = """
        QWidget {
            background-color: #333;
            color: #FFF;
        }
        QLineEdit, QPlainTextEdit {
            background-color: #555;
            color: #FFF;
            border: 1px solid #555;
        }
        QPlainTextEdit:focus {
            border: 1px solid #777;
        }
        QComboBox, QPushButton {
            background-color: #444;
            border: 1px solid #555;
            color: #FFF;
        }
        QTabBar::tab {
            background: #444;
            color: #FFF;
        }
        QTabBar::tab:selected {
            background: #555;
        }
        """
        self.setStyleSheet(dark_style)

    def run_script(self):
        selected_script = self.script_dropdown.currentText()

    
    # Return if the default option is selected.
        if selected_script == "Please Select A Script From The Dropdown Menu":
            self.console_output.setPlainText("Please select a script from the dropdown menu.")
            return

        script_name = "StressConnect.ps1" if selected_script == "Stress Connect" else ""
        api_key = self.api_key_input.text().strip()

        # Construct PowerShell command, with optional API key.
        if api_key:
            command = f'''powershell -command "& ./{script_name} -apiKey '{api_key}'"'''
        else:
            command = f'''powershell -command "& ./{script_name}"'''


        # Create and run the script thread.
        self.script_thread = RunScriptThread(command)  
        self.script_thread.signal.connect(self.handle_script_output)  
        self.script_thread.start()
        print("Running Command:", command)

       
    def save_output(self):
        # Save script output to a .csv file.
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV Files (*.csv)')
            if file_name:
                with open(file_name, 'w', newline='') as file:
                    writer = csv.writer(file, lineterminator='\n')

                    # Check if API Key is provided.
                    headers = ["Protocol", "Local Address", "Local Port", "Remote Address", "Remote Port", "State", "PID", "Process Name"]
                    if self.api_key_input.text():
                        headers.append("Malicious Verdicts")

                    writer.writerow(headers)

                    # Use the connections stored in self.connections.
                    for connection in self.connections:
                        row = [
                            connection['Protocol'],
                            connection['LocalAddress'],
                            connection['LocalPort'],
                            connection['RemoteAddress'],
                            connection['RemotePort'],
                            connection['State'],
                            connection['PID'],
                            connection['ProcessName']
                        ]
                        if 'MaliciousVerdicts' in connection:
                            row.append(str(connection['MaliciousVerdicts']))
                        writer.writerow(row)
        except Exception as e:
            # User-friendly error dialog.
            self.show_error_message("An error occurred while processing the output. Please contact support.")
            # Log the error for troubleshooting.
            with open("error_log.txt", "a") as error_file:
                error_file.write(f"An error occurred while processing the output: {str(e)}\n")

    def enable_run_button(self):
        if self.script_dropdown.currentIndex() > 0:
            self.run_button.setEnabled(True)
            self.run_button.setStyleSheet("background-color: #444;")
        else:
            self.run_button.setEnabled(False)
            self.run_button.setStyleSheet("background-color: none;")

    def enable_save_button(self):
        if self.script_output.toPlainText():
            self.save_button.setEnabled(True)
            self.save_button.setStyleSheet("background-color: #444;")
        else:
            self.save_button.setEnabled(False)
            self.save_button.setStyleSheet("background-color: none;")




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('MyLogo.ico'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())