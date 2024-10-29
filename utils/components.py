from kivymd.uix.list import ThreeLineAvatarIconListItem, TwoLineIconListItem
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty,
    ListProperty,
    DictProperty,
    NumericProperty,
    ColorProperty,
)
from kivy.lang import Builder
from kivy.clock import mainthread, Clock

Builder.load_string(
    """
<SelectList>
    CheckboxLeftWidget:
        id: item_check
        group: "wallet_check_box"
        disabled: 'True'
        active: root.checked
"""
)


class SelectList(ThreeLineAvatarIconListItem):
    disk_number = StringProperty()
    checked = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_release=lambda x: self.set_active(self.ids.item_check))
        self.secondary_font_style = "Caption"
        self.divider = None

    @mainthread
    def set_active(self, checkbox):
        checkbox.active = True


Builder.load_string(
    """
<ModelList>
    text: root.model
    secondary_text: root.name
    on_release: root.set_model(root.model)
    divider: None
"""
)


class ModelList(TwoLineIconListItem):
    model = StringProperty()
    name = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_model(self, model):
        print(model)
