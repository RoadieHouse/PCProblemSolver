"""
Info Box Widget Module

Implements a custom widget for displaying information about keyboard shortcuts
and application usage. Features an info icon with hover functionality to show
a keyboard shortcut image.
"""

import logging
from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

from app.resource_path import get_resource_path

class InfoBox(QWidget):
    """
    A custom widget that displays application usage information.
    
    Features:
    - Info icon with hover functionality
    - Keyboard shortcut information
    - Popup keyboard image on hover
    """
    
    def __init__(self, parent=None):
        """
        Initialize the InfoBox widget.
        
        Args:
            parent: Optional parent widget (default: None)
        """
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        # Create and configure the container widget
        self.info_box_container = QWidget(self)
        self.info_box_container.setMinimumHeight(40)
        self.info_box_layout = QHBoxLayout(self.info_box_container)
        self.info_box_layout.setContentsMargins(10, 5, 10, 5)

        # Create wrapper layout for left alignment
        self.wrapper_layout = QHBoxLayout()
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)
        self.wrapper_layout.setAlignment(Qt.AlignLeft)

        # Set up info icon
        self.icon_label = QLabel()
        icon_pixmap = QPixmap(get_resource_path('ui/resources/info.png'))
        scaled_pixmap = icon_pixmap.scaled(
            30, 30, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.icon_label.setPixmap(scaled_pixmap)
        self.icon_label.setStyleSheet("background: transparent;")

        # Configure hover events for info icon
        self.icon_label.setAttribute(Qt.WA_Hover, True)
        self.icon_label.installEventFilter(self)

        # Create and configure shortcut text label
        text_label = QLabel("Benutze STRG + SHIFT + LEERTASTE um einen neuen Chat zu starten")
        text_label.setFont(QFont("Arial", 11))
        text_label.setStyleSheet("color: white; background: transparent;")

        # Add widgets to info box layout
        self.info_box_layout.addWidget(self.icon_label)
        self.info_box_layout.addWidget(text_label)

        # Style the info box container
        self.info_box_container.setStyleSheet("""
            QWidget {
                background-color: rgba(50, 50, 50, 200);
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # Configure keyboard shortcut image label
        self.keyboard_label = QLabel(self.parent())
        keyboard_pixmap = QPixmap(get_resource_path('ui/resources/keyboard.png'))
        scaled_keyboard_pixmap = keyboard_pixmap.scaled(
            700, 230, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.keyboard_label.setPixmap(scaled_keyboard_pixmap)
        self.keyboard_label.resize(scaled_keyboard_pixmap.size())
        
        # Style keyboard label
        self.keyboard_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        self.keyboard_label.setAttribute(Qt.WA_TranslucentBackground)
        self.keyboard_label.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.keyboard_label.hide()

        # Set up layout hierarchy
        self.wrapper_layout.addWidget(self.info_box_container)
        self.wrapper_layout.addStretch()

        # Configure vertical layout
        self.vbox_layout = QVBoxLayout(self)
        self.vbox_layout.addLayout(self.wrapper_layout)
        self.vbox_layout.setSpacing(10)
        self.setLayout(self.vbox_layout)

    def eventFilter(self, obj, event):
        """
        Handle hover events for the info icon.
        
        Shows/hides keyboard shortcut image on hover enter/leave.
        
        Args:
            obj: Object that triggered the event
            event: Event to be handled
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if obj == self.icon_label:
            if event.type() == QEvent.HoverEnter:
                logging.info("Hovering over the info box icon")
                # Calculate and set position for keyboard image
                global_pos = self.info_box_container.mapToGlobal(
                    QPoint(0, self.info_box_container.height() + 5)
                )
                self.keyboard_label.move(global_pos)
                self.keyboard_label.show()
                self.keyboard_label.raise_()
            elif event.type() == QEvent.HoverLeave:
                self.keyboard_label.hide()
                
        return super().eventFilter(obj, event)