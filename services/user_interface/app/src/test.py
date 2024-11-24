from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, QParallelAnimationGroup
from PyQt6.QtGui import QPainter, QColor
import sys


class AnimatedCircleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)

        # Circle-related properties
        self._circle_radius = 50
        self._opacity = 0.0  # Initial opacity

        # Circle radius animation
        self.radius_animation = QPropertyAnimation(self, b"circle_radius")
        self.radius_animation.setDuration(10000)  # Animation duration
        self.radius_animation.setStartValue(50)  # Starting radius
        self.radius_animation.setEndValue(150)  # Ending radius

        # Opacity animation
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(10000)  # Animation duration
        self.opacity_animation.setStartValue(0.0)  # Fully transparent
        self.opacity_animation.setEndValue(1.0)  # Fully opaque

        # Combine animations in a parallel group
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.radius_animation)
        self.anim_group.addAnimation(self.opacity_animation)
        self.anim_group.start()

    # Getter for circle_radius
    def get_circle_radius(self):
        return self._circle_radius

    # Setter for circle_radius
    def set_circle_radius(self, radius):
        self._circle_radius = radius
        self.update()  # Trigger repaint

    # Getter for opacity
    def get_opacity(self):
        return self._opacity

    # Setter for opacity
    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()  # Trigger repaint

    # Define circle_radius and opacity as animatable properties
    circle_radius = pyqtProperty(int, get_circle_radius, set_circle_radius)
    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set opacity
        painter.setOpacity(self._opacity)

        # Draw the circle with the current radius
        painter.setBrush(QColor("blue"))
        painter.setPen(QColor("blue"))
        center_x = self.width() // 2
        center_y = self.height() // 2
        painter.drawEllipse(center_x - self._circle_radius,
                            center_y - self._circle_radius,
                            self._circle_radius * 2,
                            self._circle_radius * 2)
        painter.end()


def main():
    app = QApplication(sys.argv)
    window = AnimatedCircleWidget()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
