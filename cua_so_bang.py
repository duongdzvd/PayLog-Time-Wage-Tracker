import sys
import PySide6.QtWidgets as pw
import PySide6.QtGui as pg
from PySide6.QtCore import Qt, QEvent, Signal
import pathlib as pl
import xu_ly_tep

class MyDelegate(pw.QStyledItemDelegate):
    def __init__(self, parent = None):
        super().__init__(parent)
    
    def tinh_thoi_gian(self, model, index):
        row = index.row()
        in1_index = model.index(row, 1)
        out1_index = model.index(row, 2)
        in2_index = model.index(row, 3)
        out2_index = model.index(row, 4)
        in1 = in1_index.data(Qt.EditRole)
        in1 = 0 if in1 is None else in1
        out1 = out1_index.data(Qt.EditRole)
        out1 = 0 if out1 is None else out1
        in2 = in2_index.data(Qt.EditRole)
        in2 = 0 if in2 is None else in2
        out2 = out2_index.data(Qt.EditRole)
        out2 = 0 if out2 is None else out2
        thoi_gian_m = (out2 - in2) + (out1 - in1)
        if thoi_gian_m < 0:
            thoi_gian_m = thoi_gian_m + 1440
            return thoi_gian_m/60
        else:
            return thoi_gian_m/60
    
    def eventFilter(self, obj, event):
        if isinstance(obj, pw.QLineEdit) and event.type() == QEvent.KeyPress:
            key = event.key()
            has_sel = obj.hasSelectedText()
            pos = obj.cursorPosition()
            text_len = len(obj.text())
            if key == Qt.Key_Left and not has_sel and pos == 0:
                self.commitData.emit(obj)
                self.closeEditor.emit(obj)
                return True 
            if key == Qt.Key_Right and not has_sel and pos == text_len:
                self.commitData.emit(obj)
                self.closeEditor.emit(obj)
                return True
        return super().eventFilter(obj, event)

    def createEditor(self, parent, option, index):
        editor = pw.QLineEdit(parent)
        editor.installEventFilter(self)
        return editor
    
    def setEditorData(self, editor, index):
        minutes = index.data(Qt.EditRole)
        if minutes is None:
            editor.setText("hh:mm")
            editor.setAlignment(Qt.AlignCenter)
            return
        else:
            hh = minutes // 60
            mm = minutes % 60
            editor.setText(f"{hh:02d}:{mm:02d}")
            editor.setAlignment(Qt.AlignCenter)
    
    def setModelData(self, editor, model, index): 
        text_nhap = editor.text()
        if text_nhap.strip() == "" or text_nhap == "hh:mm":
            model.setData(index, None, Qt.EditRole)
            return
        parts = text_nhap.split(":")
        if len(parts) != 2:
            return
        try:
            hh = int(parts[0].strip())
            mm = int(parts[1].strip())
        except ValueError:
            return
        if not (0 <= hh <= 24 and 0 <= mm <= 59):
            return
        minutes = hh * 60 + mm
        model.setData(index, minutes, Qt.EditRole)
        row = index.row()
        thoi_gian_index = model.index(row, 5)
        thoi_gian = self.tinh_thoi_gian(model, index)
        model.setData(thoi_gian_index, thoi_gian, Qt.DisplayRole)
    
    def displayText(self, value, locale):
        if value is None:
            return ""
        try:
            minutes = int(value)
        except (ValueError, TypeError):
            return ""
        hh = minutes // 60
        mm = minutes % 60
        return f"{hh:02d}:{mm:02d}"

class cua_so_bang(pw.QMainWindow):
    quay_ve_start = Signal()

    def __init__(self, file_path, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Bảng tính lương")
        self.setMinimumSize(450, 720)
        self.setWindowIcon(pg.QIcon(xu_ly_tep.resource_path("assets\icon.ico")))
        wg1 = pw.QWidget()
        self.setCentralWidget(wg1)

        self.file_path = file_path
        self.is_saved = False

        lo1 = pw.QHBoxLayout()
        lo1.addStretch()
        luong_gio_label = pw.QLabel("Lương giờ:")
        self.luong_gio_box = pw.QDoubleSpinBox()
        self.luong_gio_box.valueChanged.connect(self.cap_nhat)
        self.luong_gio_box.setDecimals(1)
        self.luong_gio_box.setSingleStep(0.5)
        self.luong_gio_box.setAlignment(Qt.AlignRight)
        self.luong_gio_box.setFixedWidth(100)
        self.path_box = pw.QLineEdit()
        self.path_box.setReadOnly(True)
        self.path_box.setMinimumWidth(250)
        self.path_box.setFixedHeight(25)
        self.path_box.setText(self.file_path.stem)
        lo1.addWidget(self.path_box, 1)
        lo1.addWidget(luong_gio_label, 0)
        lo1.addWidget(self.luong_gio_box, 0)

        self.ghi_chu = pw.QTextEdit()
        self.ghi_chu.setPlaceholderText("*Ghi chú (tùy chọn)")
        self.ghi_chu.setAcceptRichText(False)
        self.ghi_chu.setMinimumWidth(250)
        self.ghi_chu.setFixedHeight(60)

        lo_23 = pw.QVBoxLayout()
        lo2 = pw.QHBoxLayout()
        lo2.addStretch()
        tong_gio_label = pw.QLabel('Tổng số giờ:')
        self.tong_gio_box = pw.QLineEdit()
        self.tong_gio_box.setReadOnly(True)
        self.tong_gio_box.setAlignment(Qt.AlignCenter)
        self.tong_gio_box.setFixedWidth(100)
        lo2.addWidget(tong_gio_label)
        lo2.addWidget(self.tong_gio_box)

        lo3 = pw.QHBoxLayout()
        lo3.addStretch()
        tong_luong_label = pw.QLabel('Tổng lương:')
        self.tong_luong_box = pw.QLineEdit()
        self.tong_luong_box.setReadOnly(True)
        self.tong_luong_box.setAlignment(Qt.AlignCenter)
        self.tong_luong_box.setFixedWidth(100)
        lo3.addWidget(tong_luong_label)
        lo3.addWidget(self.tong_luong_box)

        main_lo = pw.QVBoxLayout(wg1)
        main_lo.addLayout(lo1)
        view1 = pw.QTableView()
        view1.horizontalHeader().setSectionResizeMode(pw.QHeaderView.Stretch)
        main_lo.addWidget(view1)
        lo_23.addLayout(lo2)
        lo_23.addLayout(lo3)
        lo_ghichu = pw.QHBoxLayout()
        lo_ghichu.addWidget(self.ghi_chu)
        lo_ghichu.addLayout(lo_23)
        main_lo.addLayout(lo_ghichu)

        self.md1 = pg.QStandardItemModel()
        self.md1.dataChanged.connect(self.cap_nhat)
        header = ['Ngày', 'in', 'out', 'in', 'out', 'Thời gian']
        self.md1.setHorizontalHeaderLabels(header)

        for i in range (0,31):
            item_ngay = pg.QStandardItem()
            self.md1.setItem(i, 0, item_ngay)
            item_ngay.setData(str(i+1), Qt.DisplayRole)
            item_ngay.setEditable(False)
            item_ngay.setTextAlignment(Qt.AlignCenter)
            item_sogio = pg.QStandardItem()
            self.md1.setItem(i, 5, item_sogio)
            item_sogio.setData(0, Qt.EditRole)
            item_sogio.setData('', Qt.DisplayRole)
            item_sogio.setEditable(False)
            item_sogio.setTextAlignment(Qt.AlignCenter)
            for k in range (0, 4):
                item_gio = pg.QStandardItem()
                item_gio.setData(None, Qt.EditRole)
                item_gio.setEditable(True)
                item_gio.setTextAlignment(Qt.AlignCenter)
                self.md1.setItem(i, k + 1, item_gio)
        view1.verticalHeader().setVisible(False)
        view1.setModel(self.md1)
        delegate = MyDelegate()
        for col in range (1, 5):
            view1.setItemDelegateForColumn(col, delegate)
        self.luong_gio_box.setValue(11)
        
        separate = pw.QFrame()
        separate.setFrameShape(pw.QFrame.HLine)
        separate.setFrameShadow(pw.QFrame.Sunken)
        separate.setLineWidth(1)
        main_lo.addWidget(separate)

        self.save_button = pw.QPushButton("Lưu")
        self.save_button.setFixedHeight(40)
        self.save_button.clicked.connect(self.luu_bang)
        main_lo.addWidget(self.save_button)

    def cap_nhat(self, *args):
        tong_thoi_gian = 0
        for i in range (0, 31):
            thoi_gian_index = self.md1.index(i, 5)
            thoi_gian_value = thoi_gian_index.data(Qt.DisplayRole)
            thoi_gian_value = 0 if thoi_gian_value == '' or thoi_gian_value is None else thoi_gian_value
            tong_thoi_gian = tong_thoi_gian + float(thoi_gian_value)
        luong_gio = self.luong_gio_box.value()
        self.tong_gio_box.setText(str(tong_thoi_gian))
        self.tong_luong_box.setText(str(tong_thoi_gian * luong_gio))
    
    def xuat_data(self):
        data = {
                'luong_gio': 0,
                'bang': 
                    [
                    ],
                'tong_so_gio': 0,
                'tong_luong': 0,
                'ghi_chu' : ''
                }
        data['luong_gio'] = self.luong_gio_box.value()
        for i in range (0, 31):
            row_list = []
            for k in range (0, 5):
                so_phut_value = self.md1.index(i, k + 1).data(Qt.EditRole)
                row_list.append(so_phut_value)
            data['bang'].append(row_list)
        data['tong_so_gio'] = self.tong_gio_box.text()
        data['tong_luong'] = self.tong_luong_box.text()
        data['ghi_chu'] = self.ghi_chu.toPlainText()
        return data
    
    def nhap_data(self, data):
        self.luong_gio_box.setValue(data['luong_gio'])
        bang = data['bang']
        for i in range (0, 31):
            row = bang[i]
            for k in range (0, 5):
                value = row[k]
                index = self.md1.index(i, k + 1)
                self.md1.setData(index, value, Qt.EditRole)
        self.tong_gio_box.setText(data['tong_so_gio'])
        self.tong_luong_box.setText(data['tong_luong'])
        self.ghi_chu.setPlainText(data['ghi_chu'])

    def luu_bang(self):
        self.luu_bang_xem()
        pw.QMessageBox.information(self, "Thông báo", "Đã lưu bảng")

    def luu_bang_xem(self):
        data = self.xuat_data()
        xu_ly_tep.luu_json(self.file_path, data)
        self.quay_ve_start.emit()
        self.is_saved = True

    def mo_bang(self):
        data = xu_ly_tep.tra_json(self.file_path)
        self.nhap_data(data)

    def closeEvent(self, event):
        self.luu_bang_xem()
        event.accept()
        
if __name__ == "__main__":
    app = pw.QApplication(sys.argv)
    cs1 = cua_so_bang()
    cs1.show()
    sys.exit(app.exec())