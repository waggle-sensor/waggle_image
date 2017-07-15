import json
import pathlib
import tkinter
import tkinter.ttk as ttk

class RemoteBuildConsole:
  def __init__(self, master):
    self._config_path = pathlib.Path("./node_sw_config.json")
    self._config = self._load_config()
    self._build_gui(master)


  def _load_config(self):
    config = {}
    if self._config_path.is_file():
      with open(self._config_path) as config_file:
        config = json.loads(f.read())
    return config


  ##############################
  ### GUI Building Functions ###
  ##############################
  
  def _build_gui(self, root):
    main_frame = tkinter.Frame(root)

    self._build_menu(root)

    self._build_target_version_frame(main_frame)

    '''
    self.button = tkinter.Button(
        main_frame, text="QUIT", fg="red", command=main_frame.quit
        )
    self.button.pack(side=tkinter.TOP)
    '''

    notebook = ttk.Notebook(main_frame)

    self._build_common_page(notebook)
    self._build_nc_page(notebook)
    self._build_ep_page(notebook)

    notebook.pack(expand=1, fill="both")
    main_frame.pack()


  def _build_menu(self, master):
    menu_bar = tkinter.Menu(master)
    file_menu = tkinter.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Save", command=self._menu_handle_save)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=self._menu_handle_quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    master.config(menu=menu_bar)


  def _build_target_version_frame(self, master):
    frame = tkinter.Frame(master, borderwidth=5)
    tkinter.Label(frame, text="Target Version").pack(side=tkinter.LEFT)
    self._target_version_entry = tkinter.Entry(frame)
    self._target_version_entry.config(width=10)
    self._target_version_entry.pack(side=tkinter.LEFT)
    frame.pack()


  def _build_labeled_listbox(self, master, label):
    frame = tkinter.Frame(master, borderwidth=5)
    tkinter.Label(frame, text=label).pack(side=tkinter.TOP)
    scrollbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
    listbox = tkinter.Listbox(frame, yscrollcommand=scrollbar.set)
    listbox.config(height=10)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    listbox.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    frame.pack(side=tkinter.RIGHT)
    return listbox


  def _build_edit_frame(self, master, add_handler, remove_handler):
    frame = tkinter.Frame(master, borderwidth=5)
    button = tkinter.Button(frame, text="Add", command=add_handler)
    button.pack(side=tkinter.LEFT)
    entry = tkinter.Entry(frame)
    entry.config(width=10)
    entry.pack(side=tkinter.LEFT)
    frame.pack(side=tkinter.RIGHT)
    return entry


  def _build_common_page(self, notebook):
    page = ttk.Frame(notebook)

    self._common_apt_listbox = self._build_labeled_listbox(page, "APT Packages")
    self._common_apt_add_button = self._build_edit_frame(
      page, self._handle_common_apt_add, self._handle_common_apt_remove)

    self._common_python2_listbox = self._build_labeled_listbox(page, "Python 2 Packages")
    self._common_python2_add_button = self._build_edit_frame(
      page, self._handle_common_python2_add, self._handle_common_python2_remove)

    self._common_python3_listbox = self._build_labeled_listbox(page, "Python 3 Packages")
    self._common_python3_add_button = self._build_edit_frame(
      page, self._handle_common_python3_add, self._handle_common_python3_remove)

    notebook.add(page, text='Common')


  def _build_nc_page(self, notebook):
    page = ttk.Frame(notebook)


    notebook.add(page, text='Node Controller')


  def _build_ep_page(self, notebook):
    page = ttk.Frame(notebook)

    self.hi_there = tkinter.Button(page, text="Hello", command=self._button_handle_Hello)
    self.hi_there.pack(side=tkinter.LEFT)

    notebook.add(page, text='Edge Processor')


  ######################
  ### Event Handlers ###
  ######################

  def _menu_handle_save(self):
    pass


  def _menu_handle_quit(self):
    # TODO: suggest save if not already
    quit()


  def _button_handle_Hello(self):
    print(self._config)


  def _handle_common_apt_add(self):
    button = self._common_apt_add_button
    listbox = self._common_apt_listbox


  def _handle_common_apt_remove(self):
    button = self._common_apt_remove_button
    listbox = self._common_apt_listbox


  def _handle_common_python2_add(self):
    button = self._common_python2_add_button
    listbox = self._common_python2_listbox


  def _handle_common_python2_remove(self):
    button = self._common_python2_remove_button
    listbox = self._common_python2_listbox


  def _handle_common_python3_add(self):
    button = self._common_python3_add_button
    listbox = self._common_python3_listbox


  def _handle_common_python3_remove(self):
    button = self._common_python3_remove_button
    listbox = self._common_python3_listbox
