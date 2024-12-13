import os
import sys
import warnings
import threading
import resources_rc
from PyQt5 import QtWidgets, QtCore, QtGui
from transformers import Wav2Vec2ForCTC
from translator import Ui_Dialog  
from transfunction import translate_text, text_to_speech  
from speech_utils import recognize_speech_from_microphone, stop_speech, stop_recording_flag  

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="Some weights of the model checkpoint at facebook/wav2vec2-large-960h were not used when initializing Wav2Vec2ForCTC")
warnings.filterwarnings("ignore", message="Some weights of Wav2Vec2ForCTC were not initialized from the model checkpoint at facebook/wav2vec2-large-960h and are newly initialized")

class TranslatorApp(QtWidgets.QDialog):
    recognized_text_signal = QtCore.pyqtSignal(str)
    recording_finished_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(TranslatorApp, self).__init__()
        self.ui = Ui_Dialog()  
        self.ui.setupUi(self)
        
        self.ui.btndich.clicked.connect(self.translate_text)
        self.ui.btnmicro.clicked.connect(self.toggle_speech_micro)
        self.ui.txttienganh.textChanged.connect(self.debounce_translate_text)
        self.ui.btnloa1.clicked.connect(self.toggle_speech_en)
        self.ui.btnloa2.clicked.connect(self.toggle_speech_vi)
        self.ui.btnxoa.clicked.connect(self.clear_text)

       
        self.is_playing_en = False
        self.is_playing_vi = False
        self.is_recording = False

        
        self.recording_label = QtWidgets.QLabel(self)
        self.recording_label.setGeometry(QtCore.QRect(50, 380, 200, 30))
        self.recording_label.setText("Trạng thái ghi âm: Không ghi âm")

        
        self.recognized_text_signal.connect(self.update_text_edit)
        self.recording_finished_signal.connect(self.update_recording_status)

       
        self.debounce_timer = QtCore.QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.translate_text)

    def start_speech_recognition(self):
        global stop_recording_flag
        stop_recording_flag = False
        
        recognized_text = recognize_speech_from_microphone()
        self.recognized_text_signal.emit(recognized_text)
        self.recording_finished_signal.emit()
    
    def clear_text(self):
        reply = QtWidgets.QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn xóa tất cả văn bản?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.ui.txttienganh.clear()
            self.ui.txttiengviet.clear()

    def update_text_edit(self, text):
        if "Error" not in text:
            self.ui.txttienganh.setPlainText(text)  
        else:
            self.ui.txttienganh.setPlainText("Không thể nhận diện giọng nói.")  

    def update_recording_status(self):
        self.is_recording = False
        self.recording_label.setText("Trạng thái ghi âm: Không ghi âm")

    def translate_text(self):
        # Lấy văn bản từ ô nhập tiếng Anh
        text_to_translate = self.ui.txttienganh.toPlainText()
        
        if text_to_translate.strip():
            translated_text = translate_text(text_to_translate)
            self.ui.txttiengviet.setPlainText(translated_text)
        else:
            self.ui.txttiengviet.setPlainText("")  

    def debounce_translate_text(self):
        self.debounce_timer.start(1000)  # gọi hàm mỗi 1 giây

    def toggle_speech_en(self):
        if self.is_playing_en:
            stop_speech()
            self.is_playing_en = False
        else:
            text_to_speak = self.ui.txttienganh.toPlainText()
            
            if text_to_speak.strip():
                threading.Thread(target=text_to_speech, args=(text_to_speak, 'en')).start()
                self.is_playing_en = True

    def toggle_speech_vi(self):
        if self.is_playing_vi:
            stop_speech()
            self.is_playing_vi = False
        else:
            text_to_speak = self.ui.txttiengviet.toPlainText()
            
            if text_to_speak.strip():
                threading.Thread(target=text_to_speech, args=(text_to_speak, 'vi')).start()
                self.is_playing_vi = True

    def toggle_speech_micro(self):
        if self.is_recording:
            stop_speech()
            self.is_recording = False
            self.recording_label.setText("Trạng thái ghi âm: Không ghi âm")
        else:
            threading.Thread(target=self.start_speech_recognition).start()
            self.is_recording = True
            self.recording_label.setText("Trạng thái ghi âm: Đang ghi âm")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec_())