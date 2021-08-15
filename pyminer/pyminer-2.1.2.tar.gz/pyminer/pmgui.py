from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTextEdit

from pmgwidgets import PMGToolBar, ActionWithMessage, PMDockObject, create_icon
from utils import get_main_window, get_application


def updateSplashMsg(ext_load_status: dict):
    splash = get_application().splash
    percent = '100%' if ext_load_status.get('ext_count') == 0 \
        else round(ext_load_status.get('loaded') / ext_load_status.get('ext_count') * 100)
    try:
        msg = 'Loading:' + ext_load_status.get('ext_name') + '...' + str(percent) + '%'
        splash.showMessage(msg, Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
    except TypeError:
        return


class PMToolBarHome(PMGToolBar):
    """
    定义菜单工具栏按钮。
    """

    def __init__(self):
        super().__init__()

        self.add_tool_button(
            'button_new_script', self.tr('New Script'),
            self.tr('New Script'),
            create_icon(":/color/theme/default/icons/script.svg"))

        self.add_tool_button(
            'button_new',
            self.tr('New'),
            self.tr('New Project'),
            create_icon(":/color/theme/default/icons/new_project.svg"))

        self.add_tool_button('button_open', self.tr('Open'), self.tr('Open Script or other files'), create_icon(
            ":/color/theme/default/icons/open.svg"))

        self.addSeparator()

        self.add_tool_button(
            'button_import_data', self.tr('Get Data'), self.tr('Import data from a file'),
            create_icon(":/color/theme/default/icons/import.svg"))

        self.add_tool_button(
            'button_import_database', self.tr('Import Database'), self.tr('Import data from the database'),
            create_icon(":/color/theme/default/icons/import_database.svg"))

        self.add_buttons(3, ['button_open_variable', 'button_save_workspace', 'button_clear_workspace'],
                         [self.tr('Load Var'), self.tr('Save Var'), self.tr('Clear Var')],
                         [":/color/theme/default/icons/var_open.svg",
                          ":/color/theme/default/icons/save.svg",
                          ":/color/theme/default/icons/clear.svg"])

        self.addSeparator()
        self.add_tool_button(
            'button_browser',
            self.tr('Browser'),
            self.tr('Open Internal Browser'),
            create_icon(':/color/theme/default/icons/website.svg')
        )
        self.add_tool_button(
            'button_appstore',
            self.tr('Extensions'),
            self.tr('PIP package management'),
            create_icon(':/color/theme/default/icons/pypi_color.svg'))
        self.add_tool_button('button_help', self.tr('Help'), self.tr('Use a browser to access the help document'),
                             create_icon(
                                 ':/color/theme/default/icons/help.svg'))
        self.add_tool_button('button_community', self.tr('Community'), self.tr('Use a browser to access the community'),
                             create_icon(':/color/theme/default/icons/community.svg'))
        self.add_tool_button('button_feedback', self.tr('Feedback'),
                             self.tr('Give your feedback.\nAll feedback are greatly appreciated.'),
                             create_icon(':/color/theme/default/icons/feedback.svg'))
        self.addSeparator()

        self.add_tool_button('view_config', self.tr('Layout'), self.tr('Modify window layout'), create_icon(
            ':/color/theme/default/icons/save_layout.svg'))
        self.add_tool_button('button_settings', self.tr('Settings'), self.tr('Modify program Settings items'),
                             create_icon(
                                 ':/color/theme/default/icons/setting.svg'))
        self.addSeparator()
        self.add_tool_button(
            'button_login',
            self.tr('用户管理'),
            self.tr('用户管理'),
            create_icon(':/color/theme/default/icons/mActionUserRoleManager.svg')
        )

    def process_visibility_actions(self, e: ActionWithMessage):
        """
        处理”视图“菜单点击时触发的事件。
        """
        main_window = get_main_window()
        dws = main_window.dock_widgets
        if e.message == 'load_standard_layout':
            main_window.load_predefined_layout('standard')
        elif e.message in dws.keys():
            dws[e.message].setVisible(e.isChecked())
        elif e.message == 'lock_layout':
            main_window.set_dock_titlebar_visible(not e.isChecked())  # 如果界面锁定(True)则标题栏不可见(False)所以需要取反。

    def get_toolbar_text(self) -> str:
        return self.tr('Home')

    def bind_events(self):
        """
        绑定事件。
        """
        self.get_control_widget('button_new').clicked.connect(lambda: get_main_window().main_project_wizard_display())
        self.get_control_widget('button_clear_workspace').clicked.connect(lambda: get_main_window().clear_workspace())
        self.get_control_widget('button_settings').clicked.connect(lambda: get_main_window().main_option_display())
        self.get_control_widget('button_appstore').clicked.connect(lambda: get_main_window().main_appstore_dispaly())
        self.get_control_widget('button_help').clicked.connect(lambda: get_main_window().main_help_display())
        self.get_control_widget('button_community').clicked.connect(lambda: get_main_window().main_community_display())
        self.get_control_widget('button_feedback').clicked.connect(lambda: get_main_window().main_feedback_display())
        self.get_control_widget('button_login').clicked.connect(lambda: get_main_window().login_form_display())

        self.append_menu('button_new_script', 'Python',
                         lambda: get_main_window().main_new_script_display(),
                         create_icon(':/color/theme/default/icons/python.svg'))

        homeSiteIcon = create_icon(':/color/theme/default/icons/home_site.svg')
        self.append_menu('button_help', self.tr('Support'),
                         lambda: get_main_window().main_homesite_display(),
                         homeSiteIcon)
        helpDocIcon = create_icon(':/color/theme/default/icons/help_doc.svg')
        self.append_menu('button_help', self.tr('Reference'),
                         lambda: get_main_window().main_help_display(),
                         helpDocIcon)

        updateIcon = create_icon(':/color/theme/default/icons/check_update.svg')
        self.append_menu('button_help', self.tr('Check for updates'),
                         lambda: get_main_window().main_check_update_display(),
                         updateIcon)
        feedbackIcon = create_icon(':/color/theme/default/icons/feedback.svg')
        self.append_menu('button_help', self.tr('Give Feedback'),
                         lambda: get_main_window().main_feedback_display(),
                         feedbackIcon)
        aboutIcon = create_icon(':/color/theme/default/icons/info.svg')
        self.append_menu('button_help', self.tr('About'),
                         lambda: get_main_window().main_about_display(),
                         aboutIcon)
        self.append_menu('button_help', self.tr('Quick Start'),
                         lambda: get_main_window().first_form_display(),
                         aboutIcon)


class LogOutputConsole(QTextEdit, PMDockObject):
    pass
