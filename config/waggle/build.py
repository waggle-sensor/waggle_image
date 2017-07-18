import bisect
import inspect
import json
import pathlib
import re
import tkinter
import tkinter.ttk as ttk
import tinydb

class Configuration:
  def __init__(self):
    self._db = tinydb.TinyDB("./build_config.json")
    self._build_versions = self._db.table('Build Version')
    self._base_versions = self._db.table('Base Version')
    self._dependencies = self._db.table('Dependency')
    self._dependency_types = self._db.table('Dependency Type')
    self._deploy_configs = self._db.table('Deployment Configuration')

  def get_db(self):
    return self._db

  def add_dependency_type(self, name):
    self._dependency_types.insert({'name': name})

  def get_dependency_types(self):
    return self._dependency_types.all()

  def get_dependency_type_id(self, name):
    dep_type_entry = tinydb.Query()
    return self._dependency_types.get(dep_type_entry.name == name).eid

class VarRef():
  def __init__(self):
    self.var = None

class ConfigurationEditor:
  def __init__(self):
    self._root = tkinter.Tk()

    self._config_path = pathlib.Path("./node_sw_config.json")
    self._config = []
    self._load_config()

    # Common tab GUI variable references
    self._common_apt_listbox = VarRef()
    self._common_python2_listbox = VarRef()
    self._common_python3_listbox = VarRef()
    self._common_debian_listbox = VarRef()
    self._common_apt_entry = VarRef()
    self._common_python2_entry = VarRef()
    self._common_python3_entry = VarRef()
    self._common_debian_entry = VarRef()

    # Node Controller tab GUI variable references
    self._nc_apt_listbox = VarRef()
    self._nc_python2_listbox = VarRef()
    self._nc_python3_listbox = VarRef()
    self._nc_debian_listbox = VarRef()
    self._nc_apt_entry = VarRef()
    self._nc_python2_entry = VarRef()
    self._nc_python3_entry = VarRef()
    self._nc_debian_entry = VarRef()

    # Edge Processor tab GUI variable references
    self._ep_apt_listbox = VarRef()
    self._ep_python2_listbox = VarRef()
    self._ep_python3_listbox = VarRef()
    self._ep_debian_listbox = VarRef()
    self._ep_apt_entry = VarRef()
    self._ep_python2_entry = VarRef()
    self._ep_python3_entry = VarRef()
    self._ep_debian_entry = VarRef()

    self._version_options = None
    self._version_selection = None
    self._target_version_entry = None
    self._build_gui()


  def run(self):
    self._root.mainloop()


  def _alert(self, message):
    popup = tkinter.Toplevel()
    popup.title("Alert")
    width = 300
    height = 100
    screen_width = self._root.winfo_screenwidth()
    screen_height = self._root.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    popup.geometry('%dx%d+%d+%d' % (width, height, x, y))
    tkinter.Message(
      popup, text=message, foreground='red', width=width, justify=tkinter.CENTER).pack()
    tkinter.Button(popup, text="Dismiss", command=popup.destroy).pack()


  def _load_config(self):
    self._config = []  # array of dicts
    if self._config_path.is_file():
      with open(str(self._config_path)) as config_file:
        self._config = json.loads(config_file.read())


  def _save_config(self):
    target_version = self._target_version_entry.get()
    if not re.match('[0-9]+\.[0-9]+\.[0-9]+', target_version):
      self._alert(
        "Invalid Min. Target Version '{}'.\nUnable to create new configuration."\
        .format(target_version))

    existing_versions = sorted([d['version'] for d in self._config])
    if target_version in existing_versions:
      self._alert(
        "Min. Target version '{}' already exists.\nUnable to create new configuration."\
        .format(target_version))
      return

    subconfig = {
      "version": target_version,
      "common_apt_deps": list(self._common_apt_listbox.var.get(0, tkinter.END)),
      "common_python2_deps": list(self._common_python2_listbox.var.get(0, tkinter.END)),
      "common_python3_deps": list(self._common_python3_listbox.var.get(0, tkinter.END)),
      "common_debian_deps": list(self._common_debian_listbox.var.get(0, tkinter.END)),
      "nc_apt_deps": list(self._nc_apt_listbox.var.get(0, tkinter.END)),
      "nc_python2_deps": list(self._nc_python2_listbox.var.get(0, tkinter.END)),
      "nc_python3_deps": list(self._nc_python3_listbox.var.get(0, tkinter.END)),
      "nc_debian_deps": list(self._nc_debian_listbox.var.get(0, tkinter.END)),
      "ep_apt_deps": list(self._ep_apt_listbox.var.get(0, tkinter.END)),
      "ep_python2_deps": list(self._ep_python2_listbox.var.get(0, tkinter.END)),
      "ep_python3_deps": list(self._ep_python3_listbox.var.get(0, tkinter.END)),
      "ep_debian_deps": list(self._ep_debian_listbox.var.get(0, tkinter.END)) }
    self._config.append(subconfig)
    with open(str(self._config_path), 'w') as config_file:
      config_file.write(json.dumps(self._config))

  def _populate_subconfigs(self):
    version = self._version_selection.get()
    target_subconfig = {}
    if len(self._config) == 0:
      return
    for subconfig in self._config:
      if version == subconfig['version']:
        target_subconfig = subconfig
        break
    # TODO actually populate them...
    listboxes = [self._common_apt_listbox.var,
                self._common_python2_listbox.var,
                self._common_python3_listbox.var,
                self._common_debian_listbox.var,
                self._nc_apt_listbox.var,
                self._nc_python2_listbox.var,
                self._nc_python3_listbox.var,
                self._nc_debian_listbox.var,
                self._ep_apt_listbox.var,
                self._ep_python2_listbox.var,
                self._ep_python3_listbox.var,
                self._ep_debian_listbox.var]
    fields = ["common_apt_deps",
              "common_python2_deps",
              "common_python3_deps",
              "common_debian_deps",
              "nc_apt_deps",
              "nc_python2_deps",
              "nc_python3_deps",
              "nc_debian_deps",
              "ep_apt_deps",
              "ep_python2_deps",
              "ep_python3_deps",
              "ep_debian_deps"]
    for index,listbox in enumerate(listboxes):
      listbox.delete(0, tkinter.END)
      try:
        deps = subconfig[fields[index]]
        for dep in deps:
          listbox.insert(tkinter.END, dep)
      except Exception as e:
        pass

  def _set_package_list(self, listbox, packages):
    listbox.delete(0, tkinter.END)
    for package in packages:
      listbox.insert(tkinter.END, package)


  ##############################
  ### GUI Building Functions ###
  ##############################
  
  def _build_gui(self):
    self._root.wm_title("Waggle Build Configuration Editor")
    main_frame = tkinter.Frame(self._root)

    self._build_menu(self._root)

    self._build_version_frame(main_frame)

    notebook = ttk.Notebook(main_frame)
    self._build_common_page(notebook)
    self._build_nc_page(notebook)
    self._build_ep_page(notebook)
    notebook.pack(expand=1, fill="both")

    main_frame.pack()

    self._populate_subconfigs()


  def _build_menu(self, master):
    menu_bar = tkinter.Menu(master)
    file_menu = tkinter.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Save", command=self._menu_handle_save)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=self._menu_handle_quit)
    menu_bar.add_cascade(label="File", menu=file_menu)
    master.config(menu=menu_bar)


  def _build_version_frame(self, master):
    available_frame = tkinter.Frame(master, borderwidth=5)
    tkinter.Label(available_frame, text="Available Versions").pack(side=tkinter.LEFT)
    versions = sorted([d['version'] for d in self._config])
    self._version_selection = tkinter.StringVar(available_frame)
    if len(versions) > 0:
      self._version_selection.set(versions[-1]) # default value
    else:
      versions = [""]
      #dropdown_box = tkinter.OptionMenu(available_frame, selection, "").pack()
    self._version_selection.trace("w", self._handle_version_set)
    self._version_options = tkinter.OptionMenu(
      available_frame, self._version_selection, *tuple(versions))
    self._version_options.pack()
    available_frame.pack()

    target_frame = tkinter.Frame(master, borderwidth=5)
    tkinter.Label(target_frame, text="Min. Target Version").pack(side=tkinter.LEFT)
    self._target_version_entry = tkinter.Entry(target_frame)
    self._target_version_entry.config(width=10)
    self._target_version_entry.pack(side=tkinter.LEFT)
    target_frame.pack()


  def _build_labeled_listbox(self, master, label, listbox_ref):
    # frame = tkinter.Frame(master, borderwidth=5)
    frame = tkinter.Frame(master)
    tkinter.Label(frame, text=label).pack(side=tkinter.TOP)
    scrollbar = tkinter.Scrollbar(frame, orient=tkinter.VERTICAL)
    listbox = tkinter.Listbox(
      frame, yscrollcommand=scrollbar.set, selectmode=tkinter.EXTENDED)
    listbox.config(width=18, height=10)
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
      self, page, title, listbox_ref, entry_ref, add_handler, remove_handler):
    frame = tkinter.Frame(page, borderwidth=5)
    self._build_labeled_listbox(
      frame, "{} Dependencies".format(title), listbox_ref)
    tkinter.Button(
      frame, text="Remove", command=remove_handler)\
      .pack(side=tkinter.BOTTOM)
    self._build_add_frame(
      frame, "Add", add_handler, entry_ref)
    frame.pack(side=tkinter.LEFT)


  def _build_common_page(self, notebook):
    page = ttk.Frame(notebook)

    self._build_subconfig_frame(
      page, "APT", self._common_apt_listbox, self._common_apt_entry,
      self._handle_common_apt_add, self._handle_common_apt_remove)

    self._build_subconfig_frame(
      page, "Python 2", self._common_python2_listbox, self._common_python2_entry,
      self._handle_common_python2_add, self._handle_common_python2_remove)

    self._build_subconfig_frame(
      page, "Python 3", self._common_python3_listbox, self._common_python3_entry,
      self._handle_common_python3_add, self._handle_common_python3_remove)

    self._build_subconfig_frame(
      page, "Debian", self._common_debian_listbox, self._common_debian_entry,
      self._handle_common_debian_add, self._handle_common_debian_remove)

    notebook.add(page, text='Common')


  def _build_nc_page(self, notebook):
    page = ttk.Frame(notebook)

    self._build_subconfig_frame(
      page, "APT", self._nc_apt_listbox, self._nc_apt_entry,
      self._handle_nc_apt_add, self._handle_nc_apt_remove)

    self._build_subconfig_frame(
      page, "Python 2", self._nc_python2_listbox, self._nc_python2_entry,
      self._handle_nc_python2_add, self._handle_nc_python2_remove)

    self._build_subconfig_frame(
      page, "Python 3", self._nc_python3_listbox, self._nc_python3_entry,
      self._handle_nc_python3_add, self._handle_nc_python3_remove)

    self._build_subconfig_frame(
      page, "Debian", self._nc_debian_listbox, self._nc_debian_entry,
      self._handle_nc_debian_add, self._handle_nc_debian_remove)

    notebook.add(page, text='Node Controller')


  def _build_ep_page(self, notebook):
    page = ttk.Frame(notebook)

    self._build_subconfig_frame(
      page, "APT", self._ep_apt_listbox, self._ep_apt_entry,
      self._handle_ep_apt_add, self._handle_ep_apt_remove)

    self._build_subconfig_frame(
      page, "Python 2", self._ep_python2_listbox, self._ep_python2_entry,
      self._handle_ep_python2_add, self._handle_ep_python2_remove)

    self._build_subconfig_frame(
      page, "Python 3", self._ep_python3_listbox, self._ep_python3_entry,
      self._handle_ep_python3_add, self._handle_ep_python3_remove)

    self._build_subconfig_frame(
      page, "Debian", self._ep_debian_listbox, self._ep_debian_entry,
      self._handle_ep_debian_add, self._handle_ep_debian_remove)

    notebook.add(page, text='Edge Processor')


  ##########################
  ### GUI Event Handlers ###
  ##########################

  def _menu_handle_save(self):
    self._save_config()
    versions = sorted([d['version'] for d in self._config])
    new_version = self._target_version_entry.get()
    menu = self._version_options['menu']
    menu.delete(0, tkinter.END)
    for version in versions:
      menu.add_command(
        label=version, command=tkinter._setit(self._version_selection, version))
    self._version_selection.set(new_version)


  def _menu_handle_quit(self):
    # TODO: suggest save if not already
    quit()


  def _handle_add(self, entry, listbox):
    entry_text = entry.get()
    packages = list(listbox.get(0, tkinter.END))
    listbox.insert(bisect.bisect_left(packages, entry_text), entry_text)
    entry.delete(0, tkinter.END)


  def _handle_remove(self, listbox):
    indicies = list(map(int, listbox.curselection()))
    while len(indicies) > 0:
      listbox.delete(indicies[0], indicies[0])
      indicies = list(map(int, listbox.curselection()))

  def _handle_version_set(self, *args):
    self._populate_subconfigs()
    self._target_version_entry.delete(0,tkinter.END)

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


  def _handle_common_debian_add(self):
    entry = self._common_debian_entry.var
    listbox = self._common_debian_listbox.var
    self._handle_add(entry, listbox)


  def _handle_common_debian_remove(self):
    listbox = self._common_debian_listbox.var
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


  def _handle_nc_debian_add(self):
    entry = self._nc_debian_entry.var
    listbox = self._nc_debian_listbox.var
    self._handle_add(entry, listbox)


  def _handle_nc_debian_remove(self):
    listbox = self._nc_debian_listbox.var
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


  def _handle_ep_debian_add(self):
    entry = self._ep_debian_entry.var
    listbox = self._ep_debian_listbox.var
    self._handle_add(entry, listbox)


  def _handle_ep_debian_remove(self):
    listbox = self._ep_debian_listbox.var
    self._handle_remove(listbox)
