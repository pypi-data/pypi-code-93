# type: ignore

from __future__ import annotations

import logging
import os
import typing as t

from PyQt5 import QtCore, QtGui, QtWidgets

from n_edit import layout, model

log = logging.getLogger(__name__)


class EditorError(Exception):
    pass


class InvalidFile(EditorError):
    pass


class UnknownInputError(EditorError):
    pass


class GraphScene(QtWidgets.QGraphicsScene):
    FILE_EXTENSION = ".json"
    LAYOUT_EXTENSION = ".layout"

    def __init__(self, node_types: model.NodeLibrary, file_name: str):
        super().__init__()
        self.graph = model.Graph(node_types)
        self.layout = layout.GraphLayout(self.graph)

        if not file_name.endswith(self.FILE_EXTENSION):
            raise InvalidFile("Must be a json file")
        self.file_name = file_name
        self.layout_file_name = (
            file_name[: -len(self.FILE_EXTENSION)]
            + self.LAYOUT_EXTENSION
            + self.FILE_EXTENSION
        )
        self.load()

    def save(self) -> None:
        self.layout.save_file(self.layout_file_name)
        self.graph.save_file(self.file_name)

    def load(self) -> None:
        if not os.path.isfile(self.file_name) or not os.path.isfile(
            self.layout_file_name
        ):
            return
        self.graph.load_file(self.file_name)
        self.layout.load_file(self.layout_file_name)
        self.sync_with_graph()

    def clear(self) -> None:
        self.delete_items(self.items())

    def sync_with_graph(self) -> None:
        self.clear()
        nodes_items: dict[int, NodeItem] = {}
        for node in self.graph.nodes.values():
            layout = self.layout.get_node(node)
            nodes_items[node.id_] = NodeItem(node, layout)
            self.addItem(nodes_items[node.id_])
        for edge in self.graph.edges.values():
            start = nodes_items[edge.start.owner.id_].get_output_slot()
            end = nodes_items[edge.end.owner.id_].get_input_slot(edge.end.name)
            self.addItem(EdgeItem(start, end, edge))

    def add_node(self, node_class: str, x: float, y: float) -> None:
        node = self.graph.create_node(node_class)
        layout = self.layout.add_node(node, x, y)
        self.addItem(NodeItem(node, layout))

    def add_edge(self, start: OutputSlotItem, end: InputSlotItem) -> None:
        edge_model = self.graph.create_edge(start.output_slot, end.input_slot)
        self.addItem(EdgeItem(start, end, edge_model))

    def delete_node(self, node: NodeItem) -> None:
        self.graph.delete_node(node.model.id_)
        self.layout.delete_node(node.model)
        self.removeItem(node)

    def delete_edge(self, edge: EdgeItem) -> None:
        self.graph.delete_edge(edge.model.id_)
        edge.delete()
        self.removeItem(edge)

    def delete_items(self, items: list[QtWidgets.QGraphicsItem]) -> None:
        nodes_to_delete = [item for item in items if isinstance(item, NodeItem)]
        edges_to_delete = [item for item in items if isinstance(item, EdgeItem)]
        touching_edges = (
            edge for node in nodes_to_delete for edge in node.connected_edges()
        )
        for edge in touching_edges:
            if edge not in edges_to_delete:
                edges_to_delete.append(edge)

        for edge in edges_to_delete:
            self.delete_edge(edge)
        for node in nodes_to_delete:
            self.delete_node(node)

    def delete_selection(self) -> None:
        self.delete_items(self.selectedItems())

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Delete:
            self.delete_selection()


class GraphView(QtWidgets.QGraphicsView):
    def __init__(self, scene: GraphScene) -> None:
        super().__init__(scene)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        self.menu = QtWidgets.QMenu()

        self._add_at_position = QtCore.QPoint()
        for node_type in scene.graph.node_library.known_types():
            self._add_add_action(node_type)

    def _add_add_action(self, node_type: str) -> None:
        self.menu.addAction(node_type, self._add_node_at_cursor(node_type))

    def _add_node_at_cursor(self, node_type: str) -> t.Callable[[], None]:
        def add_node() -> None:
            position = self.mapToScene(self._add_at_position)
            self.scene().add_node(node_type, position.x(), position.y())

        return add_node

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
        return super().keyReleaseEvent(event)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self._add_at_position = self.mapFromGlobal(self.cursor().pos())  # type: ignore
        self.menu.exec(self.cursor().pos())  # type: ignore
        return super().contextMenuEvent(event)


class TopLevelItem(QtWidgets.QGraphicsItem):
    SELECT_COLOR = QtGui.QColor.fromRgb(100, 100, 200)
    FOREGROUND_COLOR = QtGui.QColor.fromRgb(60, 60, 60)
    BACKGROUND_COLOR = QtGui.QColor.fromRgb(250, 250, 250)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.setFlag(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges, True
        )

    def positionChange(self):
        pass

    def itemChange(
        self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: t.Any
    ) -> t.Any:
        if (
            change
            == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged
        ):
            self.positionChange()
        return super().itemChange(change, value)


class SlotItem(TopLevelItem):
    SIZE = 20
    DEFAULT_COLOR = QtGui.QColor.fromRgb(230, 190, 230)
    COLORS_BY_TYPE = {
        int: QtGui.QColor.fromRgb(230, 230, 20),
        float: QtGui.QColor.fromRgb(40, 200, 255),
    }

    TEXT_WIDTH = 100
    TEXT_HEIGHT = SIZE

    def __init__(self, parent: NodeItem) -> None:
        super().__init__(parent=parent)
        self.connected_edges: list[EdgeItem] = []

    def boundingRect(self) -> QtCore.QRectF:
        pen_width = 1
        return QtCore.QRectF(
            -pen_width - self.SIZE // 2,
            -pen_width - self.SIZE // 2,
            self.SIZE + pen_width,
            self.SIZE + pen_width,
        )

    def paint(  # type: ignore
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: t.Optional[QtWidgets.QWidget],
    ) -> None:
        painter.setPen(self.FOREGROUND_COLOR)
        painter.setBrush(self.DEFAULT_COLOR)
        painter.drawEllipse(-self.SIZE // 2, -self.SIZE // 2, self.SIZE, self.SIZE)

    def mousePressEvent(self, event) -> None:
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        item_under_mouse = self.scene().itemAt(event.scenePos(), self.sceneTransform())
        if isinstance(item_under_mouse, SlotItem):
            item_under_mouse.connect_to(self)

    def connect_to_output(self, output_slot: OutputSlotItem) -> None:
        pass

    def connect_to_input(self, input_slot: InputSlotItem) -> None:
        pass

    def connect_to(self, other: SlotItem) -> None:
        raise NotImplemented

    def positionChange(self):
        for edge in self.connected_edges:
            edge.prepareGeometryChange()
        return super().positionChange()


class InputSlotItem(SlotItem):
    TEXT_MARGIN = 4

    def __init__(self, parent: NodeItem, input_slot: model.InputSlot) -> None:
        super().__init__(parent)
        self.input_slot = input_slot

    def connect_to_output(self, output_slot: OutputSlotItem) -> None:
        self.connect_to(output_slot)

    def connect_to(self, other: SlotItem) -> None:
        other.connect_to_input(self)

    def _text_rect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            self.SIZE / 2 + self.TEXT_MARGIN,
            -self.SIZE / 2,
            self.TEXT_WIDTH,
            self.TEXT_HEIGHT,
        )

    def boundingRect(self) -> QtCore.QRectF:
        slot_rect = super().boundingRect()
        return slot_rect | self._text_rect()

    def paint(  # type: ignore
        self,
        painter: QtGui.QPainter,
        option,
        widget: t.Optional[QtWidgets.QWidget],
    ) -> None:
        super().paint(painter, option, widget)
        painter.drawText(
            self._text_rect(),
            QtCore.Qt.AlignmentFlag.AlignLeft,
            self.input_slot.name,
        )


class OutputSlotItem(SlotItem):
    def __init__(self, parent: NodeItem, output_slot: model.OutputSlot) -> None:
        super().__init__(parent)
        self.output_slot = output_slot

    def connect_to_input(self, input_slot: InputSlotItem) -> None:
        self.scene().add_edge(self, input_slot)

    def connect_to(self, other: SlotItem) -> None:
        other.connect_to_output(self)


class EdgeItem(TopLevelItem):
    Z_VALUE = -1

    def __init__(
        self, start_item: OutputSlotItem, end_item: InputSlotItem, model: model.Edge
    ) -> None:
        super().__init__()
        self.model = model
        self.setZValue(self.Z_VALUE)

        self.start = start_item
        self.end = end_item

        self.end.connected_edges.append(self)
        self.start.connected_edges.append(self)

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    def _end_position(self) -> QtCore.QPointF:
        try:
            return self.end.mapToScene(QtCore.QPointF(0, 0))
        except RuntimeError:
            return QtCore.QPointF(0, 0)

    def _start_position(self) -> QtCore.QPointF:
        try:
            return self.start.mapToScene(QtCore.QPointF(0, 0))
        except RuntimeError:
            return QtCore.QPointF(0, 0)

    def boundingRect(self) -> QtCore.QRectF:
        start = self._start_position()
        end = self._end_position()
        top_left_x = min(start.x(), end.x())
        top_left_y = min(start.y(), end.y())
        width = abs(start.x() - end.x())
        height = abs(start.y() - end.y())
        return QtCore.QRectF(top_left_x, top_left_y, width, height)

    def paint(  # type: ignore
        self,
        painter: QtGui.QPainter,
        option,
        widget: t.Optional[QtWidgets.QWidget],
    ) -> None:
        if self.isSelected():
            painter.setPen(QtGui.QPen(self.SELECT_COLOR, 2))
        else:
            painter.setPen(QtGui.QPen(self.FOREGROUND_COLOR, 2))

        QtGui.QPen(self.SELECT_COLOR, 10)

        distance_x = self._end_position().x() - self._start_position().x()
        path = QtGui.QPainterPath()
        path.moveTo(self._start_position())
        path.cubicTo(
            self._start_position() + QtCore.QPointF(distance_x / 2, 0),
            self._end_position() - QtCore.QPointF(distance_x / 2, 0),
            self._end_position(),
        )

        painter.drawPath(path)

    def delete(self):
        self.start.connected_edges.remove(self)
        self.end.connected_edges.remove(self)


class NodeItem(TopLevelItem):
    WIDTH = 200
    HEIGHT = 200

    def __init__(self, model: model.Node, node_layout: layout.NodeLayout) -> None:
        super().__init__()
        self.model = model
        self.layout = node_layout

        self.setPos(self.layout.position.x, self.layout.position.y)

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

        self._input_slots = self._make_input_slots()
        self._output_slots = self._make_output_slots()

    def _make_input_slots(self) -> list[InputSlotItem]:
        slots = []
        total = len(self.model.inputs)
        for i, slot in enumerate(self.model.inputs):
            item = InputSlotItem(parent=self, input_slot=slot)
            item.setPos(QtCore.QPointF(0, self.HEIGHT / (total + 1) * (i + 1)))
            slots.append(item)
        return slots

    def _make_output_slots(self) -> list[OutputSlotItem]:
        slots = []
        item = OutputSlotItem(parent=self, output_slot=self.model.output)
        item.setPos(QtCore.QPointF(self.WIDTH, self.HEIGHT / 2))
        slots.append(item)
        return slots

    def get_input_slot(self, name: str) -> InputSlotItem:
        for slot in self._input_slots:
            if slot.input_slot.name == name:
                return slot
        raise UnknownInputError(f"No such slot {name}")

    def get_output_slot(self) -> OutputSlotItem:
        return self._output_slots[0]

    def connected_edges(self) -> list[EdgeItem]:
        return [
            edge
            for slot in self._input_slots + self._output_slots  # type: ignore
            for edge in slot.connected_edges
        ]

    def delete(self) -> None:
        for input_slot in self._input_slots:
            for edge in input_slot.connected_edges:
                self.scene().removeItem(edge)

    def boundingRect(self) -> QtCore.QRectF:
        pen_width = 1
        return QtCore.QRectF(
            -pen_width / 2,
            -pen_width / 2,
            self.WIDTH + pen_width,
            self.HEIGHT + pen_width,
        )

    def _text_rect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self.WIDTH, self.HEIGHT / 5)

    def paint(  # type: ignore
        self,
        painter: QtGui.QPainter,
        option,
        widget: t.Optional[QtWidgets.QWidget],
    ) -> None:
        if self.isSelected():
            painter.setPen(self.SELECT_COLOR)
        else:
            painter.setPen(self.FOREGROUND_COLOR)
        painter.setBrush(self.BACKGROUND_COLOR)

        painter.drawRoundedRect(0, 0, self.WIDTH, self.HEIGHT, 5, 5)
        painter.drawText(
            self._text_rect(),
            QtCore.Qt.AlignmentFlag.AlignCenter,
            self.model.__class__.__name__,
        )

    def positionChange(self):
        self.layout.position.x = self.pos().x()
        self.layout.position.y = self.pos().y()
        return super().positionChange()


class EditorWindow(QtWidgets.QMainWindow):
    COMPANY = "mmEissen"
    PRODUCT = "Node Editor"

    def __init__(self, file_name: str, node_types: model.NodeLibrary) -> None:
        super().__init__()
        scene = GraphScene(node_types, file_name)
        self.graph_view = GraphView(scene)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Save", scene.save, "CTRL+S")

        self.setCentralWidget(self.graph_view)
        self.readSettings()

    def readSettings(self):
        """Read the permanent profile settings for this app"""
        settings = QtCore.QSettings(self.COMPANY, self.PRODUCT)
        pos = settings.value("pos", QtCore.QPoint(200, 200))
        size = settings.value("size", QtCore.QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        """Write the permanent profile settings for this app"""
        settings = QtCore.QSettings(self.COMPANY, self.PRODUCT)
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()
