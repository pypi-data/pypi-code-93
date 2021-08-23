from PyQt5.QtWidgets import QTableWidgetItem

from typing import Dict, Tuple, List, Optional

from plover.engine import StenoEngine
from plover.steno import Stroke
from plover.steno_dictionary import StenoDictionary, StenoDictionaryCollection
from plover.translation import Translation

from plover_next_stroke.next_stroke_ui import NextStrokeUI
from plover_next_stroke.sorting import SortingType, get_sorter


STROKE_TYPE = str
OUTLINE_TYPE = Tuple[STROKE_TYPE]


class TranslationNode:
    def __init__(self, translation: str = "") -> None:
        self.translation = translation
        self.children: Dict[STROKE_TYPE, "TranslationNode"] = {}

    def add_child(self, outline: OUTLINE_TYPE, translation: str) -> None:
        if not outline:
            return
        
        outline_len = len(outline)
        outline_head = outline[0]

        if outline_len == 1:
            if outline_head in self.children:
                self.children[outline_head].translation = translation
            else:
                self.children[outline_head] = TranslationNode(translation)
        else:
            outline_tail = outline[1:]
            if outline_head not in self.children:
                self.children[outline_head] = TranslationNode()
            
            self.children[outline_head].add_child(outline_tail, translation)
    
    def get_node(self, outline: OUTLINE_TYPE) -> Optional["TranslationNode"]:
        if not outline:
            return self

        outline_head = outline[0]
        if outline_head not in self.children:
            return None
        else:
            return self.children[outline_head].get_node(outline[1:])

    def get_suggestions(self) -> List[Tuple[OUTLINE_TYPE, str]]:
        suggestions_list = []

        if self.children:
            for stroke, node in self.children.items():
                if node.translation:
                    suggestions_list.append(([stroke], node.translation))

                node_suggestions = node.get_suggestions()
                for outline, translation in node_suggestions:
                    suggestions_list.append(([stroke] + outline, translation))
        
        return suggestions_list


class NextStrokeSuggestions(NextStrokeUI):
    _translate_tree = None
    _suggestions: List[Tuple[OUTLINE_TYPE, str]] = []
    _prev_node: Optional[TranslationNode] = None
    _page = 0

    def __init__(self, engine: StenoEngine) -> None:
        super().__init__(engine)

        engine.signal_connect("stroked", self.on_stroke)
        engine.signal_connect("dictionaries_loaded", self.on_dict_update)
        engine.signal_connect("config_changed", self.on_dict_update)
        engine.signal_connect("add_translation", self.on_dict_update)
        self.index_dictionaries()

    def update_table(self) -> None:
        top_index = self._page * self.config.page_len

        print("Updating table, config:")
        print("row height: ", self.config.row_height)
        print("page_len: ", self.config.page_len)

        page_count = (len(self._suggestions) - 1) // self.config.page_len + 1
        displayed = self._suggestions[top_index:top_index + self.config.page_len]
        display_len = len(displayed)

        for index, (outline, translation) in enumerate(displayed):
            self.suggestions_table.setItem(index, 0, QTableWidgetItem("/".join(outline)))
            self.suggestions_table.setItem(index, 1, QTableWidgetItem(translation))
        
        if display_len < self.config.page_len:
            for index in range(display_len, self.config.page_len):
                self.suggestions_table.setItem(index, 0, QTableWidgetItem(""))
                self.suggestions_table.setItem(index, 1, QTableWidgetItem(""))
        
        self.page_label.setText(f"Page {self._page + 1} of {page_count}")

    def on_stroke(self, _: tuple) -> None:
        update_suggestions = True

        if hasattr(self.engine._translator, "next_stroke_state"):
            next_stroke_state = self.engine._translator.next_stroke_state
            max_pages = (len(self._suggestions) - 1) // self.config.page_len + 1

            if next_stroke_state == "prev_page":
                self._page = (self._page - 1) % max_pages
                update_suggestions = False
            
            elif next_stroke_state == "next_page":
                self._page = (self._page + 1) % max_pages
                update_suggestions = False
            
            elif next_stroke_state == "next_stroke_reload":
                self.index_dictionaries()
            
            self.engine._translator.next_stroke_state = ""

        prev_translations: List[Translation] = self.engine.translator_state.prev()

        if prev_translations is not None and prev_translations and update_suggestions:
            translation = prev_translations[-1]
            current_outline = translation.rtfcre
            current_output = translation.english

            if current_output is None:
                self.current_translation.setPlainText(
                    f"{'/'.join(current_outline)}"
                )
            else:
                self.current_translation.setPlainText(
                    f"{'/'.join(current_outline)}: {current_output}"
                )

            tree_node = self._translate_tree.get_node(current_outline)
            suggestions = []

            if tree_node is not None:
                suggestions = tree_node.get_suggestions()
                
                if self._prev_node is not None and current_outline:
                    current_stroke = current_outline[-1]
                    traced_node = self._prev_node.get_node([current_stroke])
                    if traced_node is not None and traced_node is not tree_node:
                        suggestions += traced_node.get_suggestions()

                suggestions.sort(key=get_sorter(self.config.sorting_type))
                self._prev_node = tree_node

            self._suggestions = suggestions
            self._page = 0
        
        self.update_table()
    
    def index_dictionaries(self) -> None:
        self._translate_tree = TranslationNode()
        dictionaries: StenoDictionaryCollection = self.engine.dictionaries

        dictionary: StenoDictionary
        for dictionary in dictionaries.dicts:
            if dictionary.enabled:
                for outline, translation in dictionary.items():
                    self._translate_tree.add_child(outline, translation)

    def on_dict_update(self) -> None: 
        self.index_dictionaries()
