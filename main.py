import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame, QVBoxLayout, QSlider,QComboBox ,QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from helper_function.compile_qrc import compile_qrc
from icons_setup.compiledIcons import *
from classes.BeamViewer import BeamViewer
from classes.phasedArray import PhasedArray
from classes.controller import Controller
from classes.profileViewer import ProfileViewer
from copy import deepcopy
import numpy as np
compile_qrc()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('main.ui', self)
        self.setWindowTitle('Beam Forming')
        self.setWindowIcon(QIcon('icons_setup\icons\logo.png'))

        logoPixmap = QPixmap('icons_setup\icons\logo2.png')

        self.logoLabel = self.findChild(QLabel, 'logoLabel')
        self.logoLabel.setPixmap(logoPixmap)
        self.logoLabel.setAlignment(Qt.AlignCenter) 
        
        self.constructive_map_viewer_frame = self.findChild(QFrame,"constructiveMapFrame")
        self.constructive_map_viewer_frame_layout = QVBoxLayout()
        self.constructive_map_viewer_frame.setLayout(self.constructive_map_viewer_frame_layout)
        self.beam_Viewer = BeamViewer()
        self.constructive_map_viewer_frame_layout.addWidget(self.beam_Viewer)
        
        self.profile_viewer_frame = self.findChild(QFrame,"profileViewerFrame")
        self.profile_viewer_frame_layout = QVBoxLayout()
        self.profile_viewer_frame.setLayout(self.profile_viewer_frame_layout)
        self.profile_viewer = ProfileViewer()
        self.profile_viewer_frame_layout.addWidget(self.profile_viewer)
        
        self.phased_array = PhasedArray()
        self.phase_shift_slider = self.findChild(QSlider, "shiftSlider")
        self.phase_shift_values = [(i * np.pi * 2)/30 for i in range(30+1)]
        self.phase_shift_slider.setMinimum(0)
        self.phase_shift_slider.setMaximum(30)
        self.phase_shift_slider.valueChanged.connect(self.change_phase)
        
        
        self.frequency_slider = self.findChild(QSlider, "frequencySlider")
        self.frequency_slider.setMinimum(0)
        self.frequency_slider.setMaximum(20)
        self.frequency_slider.valueChanged.connect(self.change_frequency)
        
        self.distance_slider = self.findChild(QSlider, "distanceSlider")
        self.distance_slider.setMinimum(0)
        self.distance_slider.setMaximum(20)
        self.distance_slider.valueChanged.connect(self.set_distance_between_transmitters)
        self.number_of_transmetters_label = self.findChild(QLabel, "label_9")
        
        self.add_transmitter_button = self.findChild(QPushButton , "plusButton")
        self.add_transmitter_button.clicked.connect(self.add_transmitter)
        
        self.remove_transmitter_button = self.findChild(QPushButton , "minusButton")
        self.remove_transmitter_button.clicked.connect(self.remove_transmitter)
        
        self.mode_combobox = self.findChild(QComboBox , "comboBox")
        self.mode_combobox.currentIndexChanged.connect(self.set_mode)
        
        self.radius_slider = self.findChild(QSlider , "radiusSlider")
        self.radius_slider.setRange(1,10)
        self.radius_slider.sliderMoved.connect(self.set_radius)
        
        self.mode_combobox = self.findChild(QComboBox , "comboBox")
        self.mode_combobox.currentIndexChanged.connect(self.set_mode)
        
        self.radius_slider = self.findChild(QSlider , "radiusSlider")
        self.radius_slider.setRange(1,10)
        self.radius_slider.sliderMoved.connect(self.set_radius)
        
        self.controller = Controller(self.phased_array,self.beam_Viewer,self.profile_viewer)
        self.controller.phased_array = self.phased_array
        self.controller.beam_viewer = self.beam_Viewer
        self.controller.profile_viewer = self.profile_viewer
        self.beam_Viewer.current_phased_array = self.phased_array
        self.profile_viewer.current_phased_array = self.phased_array
        
        
        
    def change_frequency(self):
        new_frequency = self.get_frquency_slider_position()
        self.phased_array.current_frequency = deepcopy(new_frequency)
        self.controller.set_current_beam()
        
    def change_phase(self):
        new_phase = self.phase_shift_values[self.phase_shift_slider.value()]
        self.phased_array.phase_shift = deepcopy(new_phase)
        self.controller.set_current_beam()
    
    def set_mode(self , new_mode_index):
        if(new_mode_index == 0):
            self.controller.phased_array.geometry = "Linear"
        elif(new_mode_index == 1):
            self.controller.phased_array.geometry = "Curvlinear"
        self.add_transmitter()
        self.remove_transmitter()
        self.controller.set_current_beam()

    def set_distance_between_transmitters(self):
        distance_between_transmitters = self.get_distance_slider_position()
        
        circle_radius = self.radius_slider.sliderPosition()
        if(self.controller.phased_array.geometry == "Linear"):
            self.controller.calculate_linear_distance(distance_between_transmitters)
        elif (self.controller.phased_array.geometry == "Curvlinear"):
            self.controller.calcualte_angles(distance_between_transmitters ,circle_radius )
    
    def set_radius(self):
        circle_radius = self.radius_slider.sliderPosition()
        distance_between_transmitters = self.get_distance_slider_position()
        if(self.controller.phased_array.geometry == "Linear"):
            pass
        elif (self.controller.phased_array.geometry == "Curvlinear"):
            self.controller.phased_array.calcualte_angles(distance_between_transmitters , circle_radius)
        self.controller.set_current_beam()

    def add_transmitter(self):
        circle_radius = self.radius_slider.sliderPosition()
        distance_between_transmitters = self.get_distance_slider_position()
        self.number_of_transmetters_label.setText(f'{str(int(self.number_of_transmetters_label.text()) + 1)}')
        self.controller.add_transmitter(distance_between_transmitters , circle_radius)
            
    def remove_transmitter(self):
        circle_radius = self.radius_slider.sliderPosition()
        distance_between_transmitters = self.get_distance_slider_position()
        self.number_of_transmetters_label.setText(f'{str(int(self.number_of_transmetters_label.text()) - 1)}')
        self.controller.remove_transmitter(distance_between_transmitters ,circle_radius)
        
    def get_distance_slider_position(self):
        list_of_lambda_ratios = [i/2 for i in range(0,21)]
        print(list_of_lambda_ratios[self.distance_slider.value()])
        return list_of_lambda_ratios[self.distance_slider.value()]
    
    def get_frquency_slider_position(self):
        list_of_frequencies = [i for i in range(1,21)]
        return list_of_frequencies[self.frequency_slider.value()]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())