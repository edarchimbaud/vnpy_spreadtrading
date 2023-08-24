"""
Widget for spread trading.
"""

from typing import Dict, List, Any

from vnpy.event import EventEngine, Event
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import LogData
from vnpy.trader.constant import Direction
from vnpy.trader.ui import QtWidgets, QtCore, QtGui
from vnpy.trader.ui.widget import (
    BaseMonitor,
    BaseCell,
    BidCell,
    AskCell,
    TimeCell,
    PnlCell,
    DirectionCell,
    EnumCell,
)

from ..engine import (
    SpreadEngine,
    SpreadStrategyEngine,
    SpreadData,
    APP_NAME,
    EVENT_SPREAD_DATA,
    EVENT_SPREAD_POS,
    EVENT_SPREAD_LOG,
    EVENT_SPREAD_ALGO,
    EVENT_SPREAD_STRATEGY,
)


class SpreadManager(QtWidgets.QWidget):
    """"""

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.spread_engine: SpreadEngine = main_engine.get_engine(APP_NAME)

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("Spread Trading")

        self.algo_dialog: SpreadAlgoWidget = SpreadAlgoWidget(self.spread_engine)
        algo_group: QtWidgets.QGroupBox = self.create_group(
            "Trading formula", self.algo_dialog
        )
        algo_group.setMaximumWidth(300)

        self.data_monitor: SpreadDataMonitor = SpreadDataMonitor(
            self.main_engine, self.event_engine
        )
        self.log_monitor: SpreadLogMonitor = SpreadLogMonitor(
            self.main_engine, self.event_engine
        )
        self.algo_monitor: SpreadAlgoMonitor = SpreadAlgoMonitor(
            self.main_engine, self.event_engine
        )

        self.strategy_monitor: SpreadStrategyMonitor = SpreadStrategyMonitor(
            self.main_engine, self.event_engine
        )

        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid.addWidget(self.create_group("Spread name", self.data_monitor), 0, 0)
        grid.addWidget(self.create_group("Log", self.log_monitor), 1, 0)
        grid.addWidget(self.create_group("Algo", self.algo_monitor), 0, 1)
        grid.addWidget(self.create_group("Strategy", self.strategy_monitor), 1, 1)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(algo_group)
        hbox.addLayout(grid)

        self.setLayout(hbox)

    def show(self) -> None:
        """"""
        self.spread_engine.start()
        self.algo_dialog.update_class_combo()
        self.showMaximized()

    def create_group(
        self, title: str, widget: QtWidgets.QWidget
    ) -> QtWidgets.QGroupBox:
        """"""
        group: QtWidgets.QGroupBox = QtWidgets.QGroupBox()

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(widget)

        group.setLayout(vbox)
        group.setTitle(title)

        return group


class SpreadDataMonitor(BaseMonitor):
    """
    Monitor for spread data.
    """

    event_type: str = EVENT_SPREAD_DATA
    data_key: str = "name"
    sorting: bool = False

    headers: dict = {
        "name": {"display": "Name", "cell": BaseCell, "update": False},
        "bid_volume": {"display": "Bid volume", "cell": BidCell, "update": True},
        "bid_price": {"display": "Bid price", "cell": BidCell, "update": True},
        "ask_price": {"display": "Ask price", "cell": AskCell, "update": True},
        "ask_volume": {"display": "Ask volume", "cell": AskCell, "update": True},
        "net_pos": {"display": "Net position", "cell": PnlCell, "update": True},
        "datetime": {"display": "Datetime", "cell": TimeCell, "update": True},
        "price_formula": {
            "display": "Pricing formula",
            "cell": BaseCell,
            "update": False,
        },
        "trading_formula": {
            "display": "Trading formula",
            "cell": BaseCell,
            "update": False,
        },
    }

    def register_event(self) -> None:
        """
        Register event handler into event engine.
        """
        super().register_event()
        self.event_engine.register(EVENT_SPREAD_POS, self.signal.emit)


class SpreadLogMonitor(QtWidgets.QTextEdit):
    """
    Monitor for log data.
    """

    signal: QtCore.pyqtSignal = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """"""
        self.setReadOnly(True)

    def register_event(self):
        """"""
        self.signal.connect(self.process_log_event)

        self.event_engine.register(EVENT_SPREAD_LOG, self.signal.emit)

    def process_log_event(self, event: Event) -> None:
        """"""
        log: LogData = event.data
        msg: str = f"{log.time.strftime('%H:%M:%S')}\t{log.msg}"
        self.append(msg)


class SpreadAlgoMonitor(BaseMonitor):
    """
    Monitor for algo status.
    """

    event_type: str = EVENT_SPREAD_ALGO
    data_key: str = "algoid"
    sorting: bool = False

    headers: dict = {
        "algoid": {"display": "Algo ID", "cell": BaseCell, "update": False},
        "spread_name": {"display": "Spread name", "cell": BaseCell, "update": False},
        "direction": {"display": "Direction", "cell": DirectionCell, "update": False},
        "price": {"display": "Price", "cell": BaseCell, "update": False},
        "payup": {"display": "Pay up", "cell": BaseCell, "update": False},
        "volume": {"display": "Volume", "cell": BaseCell, "update": False},
        "traded_volume": {"display": "Traded volume", "cell": BaseCell, "update": True},
        "traded_price": {"display": "Traded price", "cell": BaseCell, "update": True},
        "interval": {"display": "Interval", "cell": BaseCell, "update": False},
        "count": {"display": "Count", "cell": BaseCell, "update": True},
        "status": {"display": "Status", "cell": EnumCell, "update": True},
    }

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__(main_engine, event_engine)

        self.spread_engine: SpreadEngine = main_engine.get_engine(APP_NAME)

    def init_ui(self) -> None:
        """
        Connect signal.
        """
        super().init_ui()

        self.setToolTip("Double-clicking on a cell stops the algorithm")
        self.itemDoubleClicked.connect(self.stop_algo)

    def stop_algo(self, cell) -> None:
        """
        Stop algo if cell double clicked.
        """
        algo = cell.get_data()
        self.spread_engine.stop_algo(algo.algoid)


class SpreadAlgoWidget(QtWidgets.QFrame):
    """"""

    def __init__(self, spread_engine: SpreadEngine) -> None:
        """"""
        super().__init__()

        self.spread_engine: SpreadEngine = spread_engine
        self.strategy_engine: SpreadStrategyEngine = spread_engine.strategy_engine

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("Start algorithm")
        self.setFrameShape(self.Box)
        self.setLineWidth(1)

        self.name_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()

        self.direction_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.direction_combo.addItems([Direction.LONG.value, Direction.SHORT.value])

        float_validator: QtGui.QDoubleValidator = QtGui.QDoubleValidator()

        self.price_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.price_line.setValidator(float_validator)

        self.volume_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.volume_line.setValidator(float_validator)

        int_validator: QtGui.QIntValidator = QtGui.QIntValidator()

        self.payup_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.payup_line.setValidator(int_validator)

        self.interval_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.interval_line.setValidator(int_validator)

        button_start: QtWidgets.QPushButton = QtWidgets.QPushButton("Start")
        button_start.clicked.connect(self.start_algo)

        self.mode_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Net position", "Locked position"])

        self.class_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()

        add_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Add strategy")
        add_button.clicked.connect(self.add_strategy)

        init_button: QtWidgets.QPushButton = QtWidgets.QPushButton(
            "Initialize all strategies"
        )
        init_button.clicked.connect(self.spread_engine.init_all_strategies)

        start_button: QtWidgets.QPushButton = QtWidgets.QPushButton(
            "Start all strategies"
        )
        start_button.clicked.connect(self.spread_engine.start_all_strategies)

        stop_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Stop all")
        stop_button.clicked.connect(self.spread_engine.stop_all_strategies)

        add_spread_button: QtWidgets.QPushButton = QtWidgets.QPushButton(
            "Create Spreads"
        )
        add_spread_button.clicked.connect(self.add_spread)

        remove_spread_button: QtWidgets.QPushButton = QtWidgets.QPushButton(
            "Remove spread"
        )
        remove_spread_button.clicked.connect(self.remove_spread)

        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()
        form.addRow("Spread name", self.name_line)
        form.addRow("Direction", self.direction_combo)
        form.addRow("Price", self.price_line)
        form.addRow("Volume", self.volume_line)
        form.addRow("Pay up", self.payup_line)
        form.addRow("Interval", self.interval_line)
        form.addRow("Mode", self.mode_combo)
        form.addRow(button_start)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addLayout(form)
        vbox.addStretch()
        vbox.addWidget(self.class_combo)
        vbox.addWidget(add_button)
        vbox.addWidget(init_button)
        vbox.addWidget(start_button)
        vbox.addWidget(stop_button)
        vbox.addStretch()
        vbox.addWidget(add_spread_button)
        vbox.addWidget(remove_spread_button)

        self.setLayout(vbox)

    def start_algo(self) -> None:
        """"""
        lock_str: str = self.mode_combo.currentText()
        if lock_str == "Locked position":
            lock: bool = True
        else:
            lock: bool = False

        price_text = self.price_line.text()
        volume_text = self.volume_line.text()
        payup_text = self.payup_line.text()
        interval_text = self.interval_line.text()

        for text, name in [
            (price_text, "Price"),
            (volume_text, "Volume"),
            (payup_text, "Pay up"),
            (interval_text, "Interval"),
        ]:
            if not text:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Start up failed",
                    f"Please enter [{name}]",
                    QtWidgets.QMessageBox.Ok,
                )
                return

        self.spread_engine.start_algo(
            spread_name=self.name_line.text(),
            direction=Direction(self.direction_combo.currentText()),
            price=float(price_text),
            volume=float(volume_text),
            payup=int(payup_text),
            interval=int(interval_text),
            lock=lock,
            extra={},
        )

    def add_spread(self) -> None:
        """"""
        dialog: SpreadDataDialog = SpreadDataDialog(self.spread_engine)
        dialog.exec_()

    def remove_spread(self) -> None:
        """"""
        dialog: SpreadRemoveDialog = SpreadRemoveDialog(self.spread_engine)
        dialog.exec_()

    def update_class_combo(self) -> None:
        """"""
        self.class_combo.clear()
        self.class_combo.addItems(self.spread_engine.get_all_strategy_class_names())

    def remove_strategy(self, strategy_name) -> None:
        """"""
        manager = self.managers.pop(strategy_name)
        manager.deleteLater()

    def add_strategy(self) -> None:
        """"""
        class_name: str = str(self.class_combo.currentText())
        if not class_name:
            return

        parameters: dict = self.spread_engine.get_strategy_class_parameters(class_name)
        editor: SettingEditor = SettingEditor(parameters, class_name=class_name)
        n: int = editor.exec_()

        if n == editor.Accepted:
            setting: dict = editor.get_setting()
            spread_name: str = setting.pop("spread_name")
            strategy_name: str = setting.pop("strategy_name")

            self.spread_engine.add_strategy(
                class_name, strategy_name, spread_name, setting
            )


class SpreadRemoveDialog(QtWidgets.QDialog):
    """"""

    def __init__(self, spread_engine: SpreadEngine) -> None:
        """"""
        super().__init__()

        self.spread_engine: SpreadEngine = spread_engine

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("Remove the spread")
        self.setMinimumWidth(300)

        self.name_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        names: List[SpreadData] = self.spread_engine.get_all_spread_names()
        self.name_combo.addItems(names)

        button_remove: QtWidgets.QPushButton = QtWidgets.QPushButton("Remove")
        button_remove.clicked.connect(self.remove_spread)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.name_combo)
        hbox.addWidget(button_remove)

        self.setLayout(hbox)

    def remove_spread(self) -> None:
        """"""
        spread_name: str = self.name_combo.currentText()
        self.spread_engine.remove_spread(spread_name)
        self.accept()


class SpreadStrategyMonitor(QtWidgets.QWidget):
    """"""

    signal_strategy: QtCore.pyqtSignal = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.spread_engine: SpreadEngine = main_engine.get_engine(APP_NAME)

        self.managers: Dict[str, SpreadStrategyWidget] = {}

        self.init_ui()
        self.register_event()

    def init_ui(self) -> None:
        """"""
        self.scroll_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        self.scroll_layout.addStretch()

        scroll_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        scroll_widget.setLayout(self.scroll_layout)

        scroll_area: QtWidgets.QScrollArea = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(scroll_area)
        self.setLayout(vbox)

    def register_event(self) -> None:
        """"""
        self.signal_strategy.connect(self.process_strategy_event)

        self.event_engine.register(EVENT_SPREAD_STRATEGY, self.signal_strategy.emit)

    def process_strategy_event(self, event) -> None:
        """
        Update strategy status onto its monitor.
        """
        data: dict = event.data
        strategy_name: str = data["strategy_name"]

        if strategy_name in self.managers:
            manager: SpreadStrategyWidget = self.managers[strategy_name]
            manager.update_data(data)
        else:
            manager: SpreadStrategyWidget = SpreadStrategyWidget(
                self, self.spread_engine, data
            )
            self.scroll_layout.insertWidget(0, manager)
            self.managers[strategy_name] = manager

    def remove_strategy(self, strategy_name) -> None:
        """"""
        manager: SpreadStrategyWidget = self.managers.pop(strategy_name)
        manager.deleteLater()


class SpreadStrategyWidget(QtWidgets.QFrame):
    """
    Manager for a strategy
    """

    def __init__(
        self,
        strategy_monitor: SpreadStrategyMonitor,
        spread_engine: SpreadEngine,
        data: dict,
    ) -> None:
        """"""
        super().__init__()

        self.strategy_monitor: SpreadStrategyMonitor = strategy_monitor
        self.spread_engine: SpreadEngine = spread_engine

        self.strategy_name: str = data["strategy_name"]
        self._data: dict = data

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setFixedHeight(300)
        self.setFrameShape(self.Box)
        self.setLineWidth(1)

        init_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Initialize")
        init_button.clicked.connect(self.init_strategy)

        start_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Start")
        start_button.clicked.connect(self.start_strategy)

        stop_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Stop")
        stop_button.clicked.connect(self.stop_strategy)

        edit_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Edit")
        edit_button.clicked.connect(self.edit_strategy)

        remove_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Remove")
        remove_button.clicked.connect(self.remove_strategy)

        strategy_name: str = self._data["strategy_name"]
        spread_name: str = self._data["spread_name"]
        class_name: str = self._data["class_name"]
        author: str = self._data["author"]

        label_text: str = (
            f"{strategy_name}  -  {spread_name}  ({class_name} by {author})"
        )
        label: QtWidgets.QLabel = QtWidgets.QLabel(label_text)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.parameters_monitor: StrategyDataMonitor = StrategyDataMonitor(
            self._data["parameters"]
        )
        self.variables_monitor: StrategyDataMonitor = StrategyDataMonitor(
            self._data["variables"]
        )

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(init_button)
        hbox.addWidget(start_button)
        hbox.addWidget(stop_button)
        hbox.addWidget(edit_button)
        hbox.addWidget(remove_button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)
        vbox.addWidget(self.parameters_monitor)
        vbox.addWidget(self.variables_monitor)
        self.setLayout(vbox)

    def update_data(self, data: dict) -> None:
        """"""
        self._data = data

        self.parameters_monitor.update_data(data["parameters"])
        self.variables_monitor.update_data(data["variables"])

    def init_strategy(self) -> None:
        """"""
        self.spread_engine.init_strategy(self.strategy_name)

    def start_strategy(self) -> None:
        """"""
        self.spread_engine.start_strategy(self.strategy_name)

    def stop_strategy(self) -> None:
        """"""
        self.spread_engine.stop_strategy(self.strategy_name)

    def edit_strategy(self) -> None:
        """"""
        strategy_name: str = self._data["strategy_name"]

        parameters: dict = self.spread_engine.get_strategy_parameters(strategy_name)
        editor: SettingEditor = SettingEditor(parameters, strategy_name=strategy_name)
        n: int = editor.exec_()

        if n == editor.Accepted:
            setting: dict = editor.get_setting()
            self.spread_engine.edit_strategy(strategy_name, setting)

    def remove_strategy(self) -> None:
        """"""
        result: bool = self.spread_engine.remove_strategy(self.strategy_name)

        # Only remove strategy gui manager if it has been removed from engine
        if result:
            self.strategy_monitor.remove_strategy(self.strategy_name)


class StrategyDataMonitor(QtWidgets.QTableWidget):
    """
    Table monitor for parameters and variables.
    """

    def __init__(self, data: dict) -> None:
        """"""
        super().__init__()

        self._data: dict = data
        self.cells: dict = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        labels: list = list(self._data.keys())
        self.setColumnCount(len(labels))
        self.setHorizontalHeaderLabels(labels)

        self.setRowCount(1)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(self.NoEditTriggers)

        for column, name in enumerate(self._data.keys()):
            value = self._data[name]

            cell: QtWidgets.QTableWidgetItem = QtWidgets.QTableWidgetItem(str(value))
            cell.setTextAlignment(QtCore.Qt.AlignCenter)

            self.setItem(0, column, cell)
            self.cells[name] = cell

    def update_data(self, data: dict) -> None:
        """"""
        for name, value in data.items():
            cell: QtWidgets.QTableWidgetItem = self.cells[name]
            cell.setText(str(value))


class SettingEditor(QtWidgets.QDialog):
    """
    For creating new strategy and editing strategy parameters.
    """

    def __init__(
        self, parameters: dict, strategy_name: str = "", class_name: str = ""
    ) -> None:
        """"""
        super(SettingEditor, self).__init__()

        self.parameters: dict = parameters
        self.strategy_name: str = strategy_name
        self.class_name: str = class_name

        self.edits: dict = {}

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        form: QtWidgets.QFormLayout = QtWidgets.QFormLayout()

        # Add spread_name and name edit if add new strategy
        if self.class_name:
            self.setWindowTitle(f"Add strategy: {self.class_name}")
            button_text: str = "Add"
            parameters: dict = {"strategy_name": "", "spread_name": ""}
            parameters.update(self.parameters)
        else:
            self.setWindowTitle(f"Parameter editor: {self.strategy_name}")
            button_text: str = "OK"
            parameters = self.parameters

        for name, value in parameters.items():
            type_ = type(value)

            edit: QtWidgets.QLineEdit = QtWidgets.QLineEdit(str(value))
            if type_ is int:
                validator: QtGui.QIntValidator = QtGui.QIntValidator()
                edit.setValidator(validator)
            elif type_ is float:
                validator: QtGui.QDoubleValidator = QtGui.QDoubleValidator()
                edit.setValidator(validator)

            form.addRow(f"{name} {type_}", edit)

            self.edits[name] = (edit, type_)

        button: QtWidgets.QPushButton = QtWidgets.QPushButton(button_text)
        button.clicked.connect(self.accept)
        form.addRow(button)

        self.setLayout(form)

    def get_setting(self) -> dict:
        """"""
        setting: dict = {}

        if self.class_name:
            setting["class_name"] = self.class_name

        for name, tp in self.edits.items():
            edit, type_ = tp
            value_text = edit.text()

            if type_ == bool:
                if value_text == "True":
                    value: bool = True
                else:
                    value: bool = False
            else:
                value = type_(value_text)

            setting[name] = value

        return setting


class SpreadDataDialog(QtWidgets.QDialog):
    """"""

    def __init__(self, spread_engine: SpreadEngine) -> None:
        """"""
        super().__init__()

        self.spread_engine: SpreadEngine = spread_engine

        self.leg_widgets: list = []

        self.init_ui()

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle("Create Spreads")

        self.name_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.active_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()

        self.min_volume_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.min_volume_combo.addItems(
            [
                "1",
                "0.1",
                "0.01",
                "0.001",
                "0.0001",
                "0.00001",
                "0.000001",
            ]
        )

        self.formula_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()

        self.grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()

        button_add: QtWidgets.QPushButton = QtWidgets.QPushButton("Create Spreads")
        button_add.clicked.connect(self.add_spread)

        Label: QtWidgets.QLabel = QtWidgets.QLabel

        grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        grid.addWidget(Label("Spread name"), 0, 0)
        grid.addWidget(self.name_line, 0, 1, 1, 4)
        grid.addWidget(Label("Active leg symbol"), 1, 0)
        grid.addWidget(self.active_line, 1, 1, 1, 4)
        grid.addWidget(Label("Minimum trading volume"), 2, 0)
        grid.addWidget(self.min_volume_combo, 2, 1, 1, 4)
        grid.addWidget(Label("Price formula"), 3, 0)
        grid.addWidget(self.formula_line, 3, 1, 1, 4)

        grid.addWidget(Label("Contract symbol"), 4, 1)
        grid.addWidget(Label("Direction of trading"), 4, 2)
        grid.addWidget(Label("Transaction multiplier"), 4, 3)

        int_validator: QtGui.QIntValidator = QtGui.QIntValidator()
        int_validator.setBottom(0)

        leg_count: int = 5
        variables: list = ["A", "B", "C", "D", "E"]
        for i, variable in enumerate(variables):
            symbol_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()

            direction_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
            direction_combo.addItems(["Buy", "Sell"])

            trading_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
            trading_line.setValidator(int_validator)

            grid.addWidget(Label(variable), 5 + i, 0)
            grid.addWidget(symbol_line, 5 + i, 1)
            grid.addWidget(direction_combo, 5 + i, 2)
            grid.addWidget(trading_line, 5 + i, 3)

            d: dict = {
                "variable": variable,
                "symbol": symbol_line,
                "direction": direction_combo,
                "trading": trading_line,
            }
            self.leg_widgets.append(d)

        grid.addWidget(
            Label(""),
            5 + leg_count,
            0,
        )
        grid.addWidget(button_add, 6 + leg_count, 0, 1, 5)

        self.setLayout(grid)

    def add_spread(self) -> None:
        """"""
        spread_name: str = self.name_line.text()
        if not spread_name:
            QtWidgets.QMessageBox.warning(
                self,
                "Failed to create",
                "Please enter a spread name",
                QtWidgets.QMessageBox.Ok,
            )
            return

        price_formula: str = self.formula_line.text()
        if not self.check_formula(price_formula):
            QtWidgets.QMessageBox.warning(
                self,
                "Creation failed",
                "Please enter the correct formula",
                QtWidgets.QMessageBox.Ok,
            )
            return

        active_symbol: str = self.active_line.text()
        min_volume: str = float(self.min_volume_combo.currentText())

        leg_settings: dict = {}
        for d in self.leg_widgets:
            try:
                vt_symbol: str = d["symbol"].text()
                trading_multiplier: int = int(d["trading"].text())

                if d["direction"].currentText() == "Buy":
                    trading_direction: int = 1
                else:
                    trading_direction: int = -1
                trading_multiplier: int = trading_multiplier * trading_direction

                leg_settings[vt_symbol] = {
                    "variable": d["variable"],
                    "vt_symbol": vt_symbol,
                    "trading_direction": trading_direction,
                    "trading_multiplier": trading_multiplier,
                }
            except ValueError:
                pass

        if len(leg_settings) < 2:
            QtWidgets.QMessageBox.warning(
                self,
                "Failed to create",
                "Spreads require a minimum of 2 legs.",
                QtWidgets.QMessageBox.Ok,
            )
            return

        if active_symbol not in leg_settings:
            QtWidgets.QMessageBox.warning(
                self,
                "Creation failed",
                "Active leg symbol not found in each leg",
                QtWidgets.QMessageBox.Ok,
            )
            return

        self.spread_engine.add_spread(
            spread_name,
            list(leg_settings.values()),
            price_formula,
            active_symbol,
            min_volume,
        )
        self.accept()

    def check_formula(self, formula: str) -> bool:
        """"""
        data: dict = {variable: 1 for variable in "ABCDE"}
        locals().update(data)
        try:
            result: Any = eval(formula)
            return True
        except Exception:
            return False
