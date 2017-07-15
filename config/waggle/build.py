import json
import pathlib
import tkinter
import tkinter.ttk as ttk

class VarRef():
  def __init__(self):
    self.var = None

class RemoteBuildConsole:
  def __init__(self, master):
    self._config_path = pathlib.Path("./node_sw_config.json")
    self._config = self._load_config()

    # Common tab GUI variable references
    self._common_apt_listbox = VarRef()
    self._common_python2_listbox = VarRef()
    self._common_python3_listbox = VarRef()
    self._common_apt_entry = VarRef()
    self._common_python2_entry = VarRef()
    self._common_python3_entry = VarRef()

    # Node Controller tab GUI variable references
    self._nc_apt_listbox = VarRef()
    self._nc_python2_listbox = VarRef()
    self._nc_python3_listbox = VarRef()
    self._nc_apt_entry = VarRef()
    self._nc_python2_entry = VarRef()
    self._nc_python3_entry = VarRef()

    # Edge Processor tab GUI variable references
    self._ep_apt_listbox = VarRef()
    self._ep_python2_listbox = VarRef()
    self._ep_python3_listbox = VarRef()
    self._ep_apt_entry = VarRef()
    self._ep_python2_entry = VarRef()
    self._ep_python3_entry = VarRef()

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


  def _build_labeled_listbox(self, master, label, listbox_ref):
    # frame = tkinter.Frame(master, borderwidth=5)
    frame = tkinter.Frame(master)
    tkinter.Label(frame, text=label).pack(side=tkinter.TOP)
    scrollbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
    listbox = tkinter.Listbox(frame, yscrollcommand=scrollbar.set)
    listbox.config(height=10)
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    listbox.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    frame.pack(side=tkinter.RIGHT)
    listbox_ref.var = listbox


  def _build_add_frame(self, master, label, handler, entry_ref):
    frame = tkinter.Frame(master, borderwidth=5)
    entry = tkinter.Entry(frame)
    entry.config(width=10)
    entry.pack(side=tkinter.LEFT)
    button = tkinter.Button(frame, text=label, command=handler)
    button.config()
    button.pack(side=tkinter.LEFT)
    frame.pack(side=tkinter.BOTTOM)
    entry_ref.var = entry


  def _build_subconfig_frame(\
      self, page, listbox_ref, entry_ref, add_handler, remove_handler):
    frame = tkinter.Frame(page, borderwidth=10)
    self._build_labeled_listbox(
      frame, "APT Packages", listbox_ref)
    tkinter.Button(
      frame, text="Remove", command=remove_handler)\
      .pack(side=tkinter.BOTTOM)
    self._build_add_frame(
      frame, "Add", add_handler, entry_ref)
    frame.pack(side=tkinter.LEFT)


  def _build_common_page(self, notebook):
    page = ttk.Frame(notebook)

    self._build_subconfig_frame(
      page, self._common_apt_listbox, self._common_apt_entry,
      self._handle_common_apt_add, self._handle_common_apt_remove)

    self._build_subconfig_frame(
      page, self._common_python2_listbox, self._common_python2_entry,
      self._handle_common_python2_add, self._handle_common_python2_remove)

    self._build_subconfig_frame(
      page, self._common_python3_listbox, self._common_python3_entry,
      self._handle_common_python3_add, self._handle_common_python3_remove)

    notebook.add(page, text='Common')


  def _build_nc_page(self, notebook):
    page = ttk.Frame(notebook)

    self._build_subconfig_frame(
      page, self._nc_apt_listbox, self._nc_apt_entry,
      self._handle_nc_apt_add, self._handle_nc_apt_remove)

    self._build_subconfig_frame(
      page, self._nc_python2_listbox, self._nc_python2_entry,
      self._handle_nc_python2_add, self._handle_nc_python2_remove)

    self._build_subconfig_frame(
      page, self._nc_python3_listbox, self._nc_python3_entry,
      self._handle_nc_python3_add, self._handle_nc_python3_remove)

    notebook.add(page, text='Node Controller')


  def _build_ep_page(self, notebook):
    page = ttk.Frame(notebook)

    self._build_subconfig_frame(
      page, self._ep_apt_listbox, self._ep_apt_entry,
      self._handle_ep_apt_add, self._handle_ep_apt_remove)

    self._build_subconfig_frame(
      page, self._ep_python2_listbox, self._ep_python2_entry,
      self._handle_ep_python2_add, self._handle_ep_python2_remove)

    self._build_subconfig_frame(
      page, self._ep_python3_listbox, self._ep_python3_entry,
      self._handle_ep_python3_add, self._handle_ep_python3_remove)

    notebook.add(page, text='Edge Processor')


  ##########################
  ### GUI Event Handlers ###
  ##########################

  def _menu_handle_save(self):
    pass


  def _menu_handle_quit(self):
    # TODO: suggest save if not already
    quit()


  def _button_handle_Hello(self):
    print(self._config)


  def _handle_add(self, entry, listbox):
    listbox.insert(tkinter.END, entry.get())
    entry.delete(0, tkinter.END)


  def _handle_remove(self, listbox):
    pass


  ### Common tab GUI handlers ###

  def _handle_common_apt_add(self):
    entry = self._common_apt_entry.var
    listbox = self._common_apt_listbox.var
    self._handle_add(entry, listbox)


  def _handle_common_apt_remove(self):
    listbox = self._common_apt_listbox.var
    self._handle_remove(listbox)


  def _handle_common_python2_add(self):
    entry = self._common_python2_entry.var
    listbox = self._common_python2_listbox.var
    self._handle_add(entry, listbox)


  def _handle_common_python2_remove(self):
    listbox = self._common_python2_listbox.var
    self._handle_remove(listbox)


  def _handle_common_python3_add(self):
    entry = self._common_python3_entry.var
    listbox = self._common_python3_listbox.var
    self._handle_add(entry, listbox)


  def _handle_common_python3_remove(self):
    listbox = self._common_python3_listbox.var
    self._handle_remove(listbox)


  ### Node Controller tab GUI handlers ###

  def _handle_nc_apt_add(self):
    entry = self._nc_apt_entry.var
    listbox = self._nc_apt_listbox.var
    self._handle_add(entry, listbox)


  def _handle_nc_apt_remove(self):
    listbox = self._nc_apt_listbox.var
    self._handle_remove(listbox)


  def _handle_nc_python2_add(self):
    entry = self._nc_python2_entry.var
    listbox = self._nc_python2_listbox.var
    self._handle_add(entry, listbox)


  def _handle_nc_python2_remove(self):
    listbox = self._nc_python2_listbox.var
    self._handle_remove(listbox)


  def _handle_nc_python3_add(self):
    entry = self._nc_python3_entry.var
    listbox = self._nc_python3_listbox.var
    self._handle_add(entry, listbox)


  def _handle_nc_python3_remove(self):
    listbox = self._nc_python3_listbox.var
    self._handle_remove(listbox)


  ### Common tab GUI handlers ###

  def _handle_ep_apt_add(self):
    entry = self._ep_apt_entry.var
    listbox = self._ep_apt_listbox.var
    self._handle_add(entry, listbox)


  def _handle_ep_apt_remove(self):
    listbox = self._ep_apt_listbox.var
    self._handle_remove(listbox)


  def _handle_ep_python2_add(self):
    entry = self._ep_python2_entry.var
    listbox = self._ep_python2_listbox.var
    self._handle_add(entry, listbox)


  def _handle_ep_python2_remove(self):
    listbox = self._ep_python2_listbox.var
    self._handle_remove(listbox)


  def _handle_ep_python3_add(self):
    entry = self._ep_python3_entry.var
    listbox = self._ep_python3_listbox.var
    self._handle_add(entry, listbox)


  def _handle_ep_python3_remove(self):
    listbox = self._ep_python3_listbox.var
    self._handle_remove(listbox)
