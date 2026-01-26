from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QSpinBox, QPushButton, 
                            QScrollArea, QComboBox, QDateTimeEdit, QStackedWidget)
from PyQt5.QtCore import Qt, QDateTime
import sys
import pyqtgraph as pg
from backend import (calculate_burns_score, save_score, get_all_entries, get_depression_level,
                     calculate_gad7_score, save_gad7_score, get_all_gad7_entries, get_anxiety_level)

from datetime import datetime, timedelta

class MentalHealthTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mental Health Tracker")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Questionnaire selection
        self.questionnaire_select = QComboBox()
        self.questionnaire_select.addItems(["Burns Depression Checklist", "GAD-7 Anxiety Questionnaire"])
        self.questionnaire_select.currentIndexChanged.connect(self.switch_questionnaire)
        self.layout.addWidget(self.questionnaire_select)

        # Create stacked widget for questionnaires
        self.questionnaire_stack = QStackedWidget()
        self.burns_widget = self.create_burns_questionnaire()
        self.gad7_widget = self.create_gad7_questionnaire()
        self.questionnaire_stack.addWidget(self.burns_widget)
        self.questionnaire_stack.addWidget(self.gad7_widget)
        
        self.graph_widget = self.create_graph()
        
        # Add both widgets to main layout
        self.layout.addWidget(self.questionnaire_stack)
        self.layout.addWidget(self.graph_widget)
        
        # Toggle button at the bottom
        self.toggle_button = QPushButton("Switch to Graph View")
        self.toggle_button.clicked.connect(self.toggle_view)
        self.layout.addWidget(self.toggle_button)
        
        # Initially hide the graph
        self.graph_widget.hide()

    def switch_questionnaire(self, index):
        self.questionnaire_stack.setCurrentIndex(index)
        
    def create_burns_questionnaire(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.burns_responses = []
        questions = [
            "1. Feeling sad or down in the dumps", "2. Feeling unhappy or blue", "3. Crying spells or tearfulness",
            "4.Feeling discouraged", "5.Feeling hopeless", "6.Low self-esteem", "7.Feeling worthless or inadequate",
            "8.Guilt or shame", "9.Criticizing yourself or others", "10.Difficulty making decisions",
            "11.Loss of interest in family, friends or colleagues", "12.Loneliness", "13.Spending less time with family or friends",
            "14.Loss of motivation", "15.Loss of interest in work or other activities", "16.Avoiding work or other activities",
            "17.Loss of pleasure or satisfaction in life", "18.Feeling tired", "19.Difficulty sleeping or sleeping too much",
            "20.Decreased or increased appetite", "21.Loss of interest in sex", "22.Worrying about your health",
            "23.Do you have any suicidal thoughts?", "24. Would you like to end your life?", "25. Do you have a plan for harming yourself?"
        ]
        
        scale_label = QLabel("Rating Scale: 0=Not At All, 1=Somewhat, 2=Moderately, 3=A Lot, 4=Extremely")
        scroll_layout.addWidget(scale_label)
        
        for question in questions:
            q_widget = QWidget()
            q_layout = QHBoxLayout(q_widget)
            label = QLabel(question)
            label.setWordWrap(True)
            spinbox = QSpinBox()
            spinbox.setRange(0, 4)
            q_layout.addWidget(label)
            q_layout.addWidget(spinbox)
            self.burns_responses.append(spinbox)
            scroll_layout.addWidget(q_widget)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        submit_btn = QPushButton("Calculate Score")
        submit_btn.clicked.connect(self.calculate_burns_result)
        layout.addWidget(submit_btn)
        
        self.burns_result_label = QLabel()
        layout.addWidget(self.burns_result_label)
        
        return widget

    def create_gad7_questionnaire(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.gad7_responses = []
        questions = [
            "1. Feeling nervous, anxious, or on edge",
            "2. Not being able to stop or control worrying",
            "3. Worrying too much about different things",
            "4. Trouble relaxing",
            "5. Being so restless that it is hard to sit still",
            "6. Becoming easily annoyed or irritable",
            "7. Feeling afraid, as if something awful might happen"
        ]

        scale_label = QLabel("Rating Scale: 0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day")
        scroll_layout.addWidget(scale_label)

        for question in questions:
            q_widget = QWidget()
            q_layout = QHBoxLayout(q_widget)
            label = QLabel(question)
            label.setWordWrap(True)
            spinbox = QSpinBox()
            spinbox.setRange(0, 3)
            q_layout.addWidget(label)
            q_layout.addWidget(spinbox)
            self.gad7_responses.append(spinbox)
            scroll_layout.addWidget(q_widget)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        submit_btn = QPushButton("Calculate Score")
        submit_btn.clicked.connect(self.calculate_gad7_result)
        layout.addWidget(submit_btn)

        self.gad7_result_label = QLabel()
        layout.addWidget(self.gad7_result_label)

        return widget
        
    def create_graph(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)

        self.graph_select = QComboBox()
        self.graph_select.addItems(["Depression (Burns)", "Anxiety (GAD-7)"])
        self.graph_select.currentTextChanged.connect(self.update_graph)
        controls_layout.addWidget(QLabel("Graph:"))
        controls_layout.addWidget(self.graph_select)

        self.time_filter = QComboBox()
        self.time_filter.addItems(["All Time", "Last Week", "Last Month", "Last Year", "Custom"])
        self.time_filter.currentTextChanged.connect(self.update_graph)
        
        self.date_from = QDateTimeEdit()
        self.date_to = QDateTimeEdit()
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.date_to.setDateTime(QDateTime.currentDateTime())
        
        controls_layout.addWidget(QLabel("Time Range:"))
        controls_layout.addWidget(self.time_filter)
        controls_layout.addWidget(QLabel("From:"))
        controls_layout.addWidget(self.date_from)
        controls_layout.addWidget(QLabel("To:"))
        controls_layout.addWidget(self.date_to)
        
        layout.addWidget(controls_widget)
        
        self.graph = pg.PlotWidget()
        self.graph.setBackground('w')
        self.graph.setLabel('bottom', 'Date')
        
        self.graph.showGrid(x=True, y=True)
        self.graph.setMouseEnabled(x=False, y=False)
        self.graph.setMenuEnabled(False)
        
        date_axis = pg.DateAxisItem(orientation='bottom')
        self.graph.setAxisItems({'bottom': date_axis})
        
        layout.addWidget(self.graph)
        return widget

    def calculate_burns_result(self):
        scores = [spin.value() for spin in self.burns_responses]
        total_score = calculate_burns_score(scores)
        save_score(total_score)
        
        self.burns_result_label.setText(f"Your total score is: {total_score}\n"
                                     f"Depression Level: {get_depression_level(total_score)}")
        
    def calculate_gad7_result(self):
        scores = [spin.value() for spin in self.gad7_responses]
        total_score = calculate_gad7_score(scores)
        save_gad7_score(total_score)
        
        self.gad7_result_label.setText(f"Your total score is: {total_score}\n"
                                    f"Anxiety Level: {get_anxiety_level(total_score)}")
        
    def update_graph(self):
        graph_type = self.graph_select.currentText()
        
        if "Depression" in graph_type:
            entries = get_all_entries()
            self.graph.setLabel('left', 'Depression Score')
            self.graph.setYRange(0, 100, padding=0)
            y_axis = self.graph.getAxis('left')
            y_ticks = [(i, str(i)) for i in range(0, 101, 25)]
            y_axis.setTicks([y_ticks])
        else:
            entries = get_all_gad7_entries()
            self.graph.setLabel('left', 'Anxiety Score')
            self.graph.setYRange(0, 21, padding=0)
            y_axis = self.graph.getAxis('left')
            y_ticks = [(i, str(i)) for i in range(0, 22, 3)]
            y_axis.setTicks([y_ticks])

        filter_type = self.time_filter.currentText()
        now = datetime.now()
        
        if filter_type == "Last Week":
            start_date = now - timedelta(days=7)
        elif filter_type == "Last Month":
            start_date = now - timedelta(days=30)
        elif filter_type == "Last Year":
            start_date = now - timedelta(days=365)
        elif filter_type == "Custom":
            start_date = self.date_from.dateTime().toPyDateTime()
            now = self.date_to.dateTime().toPyDateTime()
        else:  # All Time
            start_date = datetime.min
        
        filtered_entries = [(entry[1], datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S'))
                        for entry in entries
                        if datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S') >= start_date
                        and datetime.strptime(entry[3], '%Y-%m-%d %H:%M:%S') <= now]
        
        self.graph.clear()
        if filtered_entries:
            scores, dates = zip(*filtered_entries)
            timestamps = [d.timestamp() for d in dates]
            
            self.graph.plot(timestamps, scores, 
                        symbol='o',
                        symbolSize=10,
                        symbolBrush='b',
                        pen=pg.mkPen('b', width=2))
            
    def toggle_view(self):
        if self.questionnaire_stack.isVisible():
            self.questionnaire_stack.hide()
            self.questionnaire_select.hide()
            self.graph_widget.show()
            self.toggle_button.setText("Switch to Questionnaire")
            self.update_graph()
        else:
            self.questionnaire_stack.show()
            self.questionnaire_select.show()
            self.graph_widget.hide()
            self.toggle_button.setText("Switch to Graph View")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MentalHealthTracker()
    window.show()
    sys.exit(app.exec_())
