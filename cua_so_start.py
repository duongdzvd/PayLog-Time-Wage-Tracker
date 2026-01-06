import sys
import PySide6.QtWidgets as pw
import PySide6.QtGui as pg
from PySide6.QtCore import Qt, QSettings
import pathlib as pl
import xu_ly_tep
import cua_so_bang

class cua_so_start(pw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PayLog — Time & Wage Tracker")
        self.setMinimumSize(450, 700)
        self.setWindowIcon(pg.QIcon(xu_ly_tep.resource_path("assets\icon.ico")))

        main_wg = pw.QWidget()
        self.setCentralWidget(main_wg)
        main_lo = pw.QVBoxLayout()
        main_wg.setLayout(main_lo)
        workspace_label = pw.QLabel("Workspace (thư mục chứa các bảng):")
        main_lo.addWidget(workspace_label)

        lo1 = pw.QHBoxLayout()
        main_lo.addLayout(lo1)
        icon = pw.QApplication.style().standardIcon(pw.QStyle.SP_DirOpenIcon)
        self.path_box = pw.QLineEdit()
        self.path_box.setReadOnly(True)
        self.path_box.setMinimumWidth(300)
        self.path_box.setFixedHeight(25)
        self.btn_open_workspace = pw.QPushButton("Mở thư mục…")
        self.btn_open_workspace.clicked.connect(self.mo_thu_muc)
        self.btn_open_workspace.setIcon(icon)
        lo1.addWidget(self.path_box)
        lo1.addWidget(self.btn_open_workspace)
        separate = pw.QFrame()
        separate.setFrameShape(pw.QFrame.HLine)
        separate.setFrameShadow(pw.QFrame.Sunken)
        separate.setLineWidth(1)
        main_lo.addWidget(separate)

        self.view1 = pw.QTableView()
        self.view1.horizontalHeader().setSectionResizeMode(pw.QHeaderView.Stretch)
        self.view1.doubleClicked.connect(self.double_click)
        self.view1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view1.customContextMenuRequested.connect(self.chuot_phai)
        main_lo.addWidget(self.view1)

        self.md = pg.QStandardItemModel()
        header = ['Stt', 'Bảng', 'Tổng số giờ', 'Tổng lương']
        self.md.setHorizontalHeaderLabels(header)
        self.view1.setModel(self.md)
        self.view1.verticalHeader().setVisible(False)

        separate = pw.QFrame()
        separate.setFrameShape(pw.QFrame.HLine)
        separate.setFrameShadow(pw.QFrame.Sunken)
        separate.setLineWidth(1)
        main_lo.addWidget(separate)

        self.setnew_button = pw.QPushButton("Thêm bảng mới +")
        self.setnew_button.setFixedHeight(40)
        self.setnew_button.clicked.connect(self.tao_bang_moi)
        main_lo.addWidget(self.setnew_button)

        self.bang_windows = []
        self.new_x = 0

        header = self.view1.horizontalHeader()
        header.setSectionResizeMode(0, pw.QHeaderView.Fixed)
        header.setSectionResizeMode(1, pw.QHeaderView.Stretch)
        header.setSectionResizeMode(2, pw.QHeaderView.Fixed)
        header.setSectionResizeMode(3, pw.QHeaderView.Fixed)
        self.view1.setColumnWidth(0, 30)   
        self.view1.setColumnWidth(2, 80)  
        self.view1.setColumnWidth(3, 80)

        self.path_obj = None 
        self.tai_cauhinh()
        self.tai_du_lieu()

    def tai_du_lieu(self):
        if not isinstance(self.path_obj, pl.Path) or not self.path_obj.exists():
            return
        json_files_list = list(self.path_obj.glob("*.json"))
        self.path_box.setText(str(self.path_obj))

        self.md.removeRows(0, self.md.rowCount())

        for i in range(0, len(json_files_list)):
            item_stt = pg.QStandardItem()
            self.md.setItem(i, 0, item_stt)
            item_stt.setData(str(i+1), Qt.DisplayRole)
            item_stt.setEditable(False)
            item_stt.setTextAlignment(Qt.AlignCenter)
            
            current_file = json_files_list[i]
            item_file = pg.QStandardItem()
            self.md.setItem(i, 1, item_file)
            item_file.setData('   ' + str(current_file.stem), Qt.DisplayRole)
            item_file.setEditable(False)
            
            tong_gio, tong_luong = self.lay_data(current_file)
            item_tong_gio = pg.QStandardItem()
            self.md.setItem(i, 2, item_tong_gio)
            item_tong_gio.setEditable(False)
            item_tong_gio.setTextAlignment(Qt.AlignCenter)
            item_tong_gio.setData(tong_gio, Qt.DisplayRole)

            item_tong_luong = pg.QStandardItem()
            self.md.setItem(i, 3, item_tong_luong)
            item_tong_luong.setEditable(False)
            item_tong_luong.setTextAlignment(Qt.AlignCenter)
            item_tong_luong.setData(tong_luong, Qt.DisplayRole)

    def mo_thu_muc(self):
        self.workspace = pw.QFileDialog.getExistingDirectory(self, "Chọn thư mục chứa bảng")
        self.path_obj = pl.Path(self.workspace)
        self.tai_du_lieu()

    def lay_data(self, path):
        data = xu_ly_tep.tra_json(path)
        return data['tong_so_gio'], data['tong_luong']
    
    def tai_cauhinh(self):
        settings = QSettings('x', 'y')
        path_str = settings.value('last_folder', '')
        if path_str:
            self.path_obj = pl.Path(path_str)
        else:
            self.path_obj = None

    def luu_cauhinh(self):
        settings = QSettings('x', 'y')
        if self.path_obj is not None:
            settings.setValue('last_folder', str(self.path_obj))

    def closeEvent(self, event):
        self.luu_cauhinh()
        event.accept()

    def tao_bang_moi(self):
        if self.path_obj == pl.Path(''):
            self.mo_thu_muc()
        if self.path_obj == pl.Path(''):
            return
        file_name, ok_ornot = pw.QInputDialog.getText(self, 'Hãy nhập tên bảng', 'Tên bảng:')
        if not ok_ornot:
            return
        if not file_name or file_name == ".json": 
            pw.QMessageBox.warning(self, 'Lỗi', 'Tên bảng không hợp lệ')
            return
        new_file_path = self.path_obj / f"{file_name}.json"
        sub_cua_so_bang = cua_so_bang.cua_so_bang(file_path = new_file_path, parent = self)
        sub_cua_so_bang.quay_ve_start.connect(self.tai_du_lieu)
        cuasostart_vitri = self.pos()
        sub_cua_so_bang.move(cuasostart_vitri.x() + self.new_x + 300, cuasostart_vitri.y() - 10)
        self.new_x = self.new_x + 50
        sub_cua_so_bang.show()
        sub_cua_so_bang.raise_()
        sub_cua_so_bang.activateWindow()
        self.bang_windows.append(sub_cua_so_bang)
    
    def double_click(self, index):
        row = index.row()
        file_name_index = self.md.index(row, 1)
        file_name = file_name_index.data(Qt.DisplayRole)
        file_name = file_name.strip()
        file_path = self.path_obj / f"{file_name}.json"
        sub_cua_so_bang = cua_so_bang.cua_so_bang(file_path = file_path, parent = self)
        sub_cua_so_bang.mo_bang()
        sub_cua_so_bang.quay_ve_start.connect(self.tai_du_lieu)
        cuasostart_vitri = self.pos()
        sub_cua_so_bang.move(cuasostart_vitri.x() + self.new_x + 300, cuasostart_vitri.y() - 10)
        self.new_x = self.new_x + 50
        sub_cua_so_bang.show()
        sub_cua_so_bang.raise_()
        sub_cua_so_bang.activateWindow()
        self.bang_windows.append(sub_cua_so_bang)
    
    def chuot_phai(self, pos):
        index = self.view1.indexAt(pos)
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        COL_TEN_FILE = 1
        if col != COL_TEN_FILE:
            return
        self.view1.selectRow(row)

        menu = pw.QMenu(self)
        act_open = pg.QAction("Mở", self)
        act_rename = pg.QAction("Đổi tên", self)
        act_delete = pg.QAction("Xóa", self)
        menu.addAction(act_open)
        menu.addAction(act_rename)
        menu.addAction(act_delete)

        chosen_action = menu.exec(self.view1.viewport().mapToGlobal(pos))

        if chosen_action == act_open:
            self.double_click(index)

        elif chosen_action == act_rename:
            self.chuot_phai_doiten(row)

        elif chosen_action == act_delete:
            self.chuot_phai_xoa(row)
    
    def chuot_phai_xoa(self, row):
        file_name_index = self.md.index(row, 1)
        file_name = file_name_index.data(Qt.DisplayRole)
        file_name = file_name.strip()
        file_path = self.path_obj / f"{file_name}.json"

        ret = pw.QMessageBox.question(self, 'Xác nhận xóa', f'Bạn có chắc muốn xóa file:\n{file_name} ?', pw.QMessageBox.Yes | pw.QMessageBox.No, pw.QMessageBox.No)
        if ret != pw.QMessageBox.Yes:
            return
        
        try:
            file_path.unlink()
        except Exception as e:
            pw.QMessageBox.critical(self, 'Lỗi', f'Không thể xóa file:\n{e}')
            return
        self.tai_du_lieu()

    def chuot_phai_doiten(self, row):
        file_name_index = self.md.index(row, 1)
        file_name = file_name_index.data(Qt.DisplayRole)
        file_name = file_name.strip()
        file_path = self.path_obj / f'{file_name}.json'

        new_name, ok = pw.QInputDialog.getText(self, 'Đổi tên bảng', 'Nhập tên mới:')
        if not ok:
            return
        
        new_name = new_name.strip()
        if not new_name:
            pw.QMessageBox.warning(self, 'Lỗi', 'Tên file không được để trống')
            return
        new_path = self.path_obj / f"{new_name}.json"
        if new_path == file_path:
            return
        
        if new_path.exists():
            pw.QMessageBox.warning(self, 'Lỗi', 'Đã tồn tại file cùng tên')
            return
        
        try:
            file_path.rename(new_path)
        except Exception as e:
            pw.QMessageBox.critical(self, 'Lỗi', f'Không thể đổi tên file:\n{e}')
            return
        self.tai_du_lieu()

if __name__ == "__main__":
    app = pw.QApplication(sys.argv)
    app.setWindowIcon(pg.QIcon(xu_ly_tep.resource_path("assets\icon.ico")))
    cs1 = cua_so_start()
    cs1.show()
    sys.exit(app.exec())