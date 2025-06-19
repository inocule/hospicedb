# FILENAME 2: modern_hospice_db
import customtkinter as ctk
from tkinter import ttk, Menu, messagebox
from db_operations import DatabaseOperations
import sqlite3
from constants import (
    WINDOW_SIZE, TITLE, FONTS, BUTTONS, MAPPINGS,
    TABLE_STRUCTURES, THEME_CONFIG
)
import datetime

class UndoRedoEntry(ctk.CTkEntry):
    """Custom entry widget with undo/redo support"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize undo stack
        self._undo_stack = []
        self._redo_stack = []
        self._current_text = ""
        
        # Bind text changes
        self._entry.bind('<<Modified>>', self._on_modify)
        
        # Bind undo/redo shortcuts
        self.bind('<Control-z>', self._undo)
        self.bind('<Control-y>', self._redo)
        
    def _on_modify(self, event=None):
        """Handle text modifications"""
        new_text = self._entry.get()
        if new_text != self._current_text:
            self._undo_stack.append(self._current_text)
            self._current_text = new_text
            self._redo_stack.clear()  # Clear redo stack on new changes
        self._entry.edit_modified(False)  # Reset modified flag
        
    def _undo(self, event=None):
        """Undo last change"""
        if self._undo_stack:
            # Save current text for redo
            self._redo_stack.append(self._current_text)
            # Pop and apply last undo state
            self._current_text = self._undo_stack.pop()
            self._entry.delete(0, "end")
            self._entry.insert(0, self._current_text)
        return "break"
        
    def _redo(self, event=None):
        """Redo last undone change"""
        if self._redo_stack:
            # Save current text for undo
            self._undo_stack.append(self._current_text)
            # Pop and apply last redo state
            self._current_text = self._redo_stack.pop()
            self._entry.delete(0, "end")
            self._entry.insert(0, self._current_text)
        return "break"

class ModernHospital:
    def __init__(self):
        # Initialize window
        self.root = ctk.CTk()
        self.root.title(TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # Set initial theme
        self.current_theme = "Light"
        ctk.set_appearance_mode(THEME_CONFIG[self.current_theme]["appearance_mode"])

        # Initialize database and variables
        self.db = DatabaseOperations()
        self._init_variables()
        
        # Store dropdown menu references
        self.dropdowns = {}
        
        # Admin view flag
        self.is_admin_view = False
        
        # Store text widget references for undo/redo
        self.text_widgets = {}
        
        # Setup UI
        self._setup_menu()
        self._setup_gui()
        self.fetch_data()

    def _init_variables(self):
        """Initialize StringVar variables for form fields"""
        self.variables = {}
        for table in TABLE_STRUCTURES.values():
            for col in table:
                if col not in self.variables:
                    self.variables[col] = ctk.StringVar()
        
        # Set defaults
        self.variables['civilStatus'].set("S")
        self.variables['education'].set("N")

    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "Light" if self.current_theme == "Dark" else "Dark"
        ctk.set_appearance_mode(THEME_CONFIG[self.current_theme]["appearance_mode"])

        # Update Treeview style based on theme
        style = ttk.Style()
        treeview_style = THEME_CONFIG[self.current_theme]["treeview"]
        style.configure("Treeview", **treeview_style)
        style.configure("Treeview.Heading", **treeview_style)

    def _toggle_admin_view(self):
        """Toggle admin view and update the interface"""
        self.is_admin_view = not self.is_admin_view
        
        # If enabling admin view, create the Credential table
        if self.is_admin_view and "Credential" not in self.tables:
            tab = ctk.CTkFrame(self.table_notebook)
            self.table_notebook.add(tab, text="Credential")

            # Scrollbars
            scroll_x = ttk.Scrollbar(tab, orient="horizontal")
            scroll_y = ttk.Scrollbar(tab, orient="vertical")
            scroll_x.pack(side="bottom", fill="x")
            scroll_y.pack(side="right", fill="y")

            # Table
            style = ttk.Style()
            style.theme_use('default')
            
            # Apply current theme's style
            treeview_style = THEME_CONFIG[self.current_theme]["treeview"]
            style.configure("Treeview", **treeview_style)
            style.configure("Treeview.Heading", **treeview_style)

            table = ttk.Treeview(
                tab,
                columns=TABLE_STRUCTURES["Credential"],
                xscrollcommand=scroll_x.set,
                yscrollcommand=scroll_y.set,
                selectmode='extended'
            )

            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

            for col in TABLE_STRUCTURES["Credential"]:
                table.heading(col, text=col.replace('_', ' ').title())
                table.column(col, width=120, anchor="center")

            table["show"] = "headings"
            table.pack(fill="both", expand=True)
            
            # Add Ctrl+A binding for selecting all rows
            def select_all_rows(event, tree=table):
                tree.selection_set(tree.get_children())
                return "break"
            
            table.bind('<Control-a>', select_all_rows)
            table.bind('<Command-a>', select_all_rows)  # macOS
            
            self.tables["Credential"] = table
        
        # If disabling admin view, remove the Credential table
        elif not self.is_admin_view and "Credential" in self.tables:
            tab_id = self.table_notebook.select()
            if self.table_notebook.tab(tab_id, "text") == "Credential":
                # If currently on Credential tab, switch to another tab first
                for tab in self.table_notebook.tabs():
                    if self.table_notebook.tab(tab, "text") != "Credential":
                        self.table_notebook.select(tab)
                        break
            
            # Find and remove the Credential tab
            for tab in self.table_notebook.tabs():
                if self.table_notebook.tab(tab, "text") == "Credential":
                    self.table_notebook.forget(tab)
                    break
            
            # Remove from tables dict
            del self.tables["Credential"]
        
        # Refresh data to show/hide Credential table
        self.fetch_data()

    def _handle_undo(self, event=None):
        """Handle undo for the currently focused widget"""
        focused = self.root.focus_get()
        
        # Handle SQL text widget
        if focused == self.sql_text._textbox:
            try:
                self.sql_text._textbox.edit_undo()
            except:
                pass
        # Handle custom entry widgets
        elif isinstance(focused, UndoRedoEntry):
            focused._undo()
            
        return "break"

    def _handle_redo(self, event=None):
        """Handle redo for the currently focused widget"""
        focused = self.root.focus_get()
        
        # Handle SQL text widget
        if focused == self.sql_text._textbox:
            try:
                self.sql_text._textbox.edit_redo()
            except:
                pass
        # Handle custom entry widgets
        elif isinstance(focused, UndoRedoEntry):
            focused._redo()
            
        return "break"

    def _setup_menu(self):
        """Setup the menu bar"""
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # View menu
        view_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Switch Theme", 
                            command=self._toggle_theme)
        view_menu.add_command(label="Toggle Admin View",
                            command=self._toggle_admin_view)
        
        # Edit menu
        edit_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo\t (Ctrl+Z)", 
                            command=self._handle_undo)
        edit_menu.add_command(label="Redo\t (Ctrl+Y)", 
                            command=self._handle_redo)
        
        # Tools menu
        tools_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Reset All Tables", 
                             command=self._drop_tables)
        
        # Add global bindings for undo/redo
        self.root.bind_all('<Control-z>', self._handle_undo)
        self.root.bind_all('<Control-y>', self._handle_redo)

    def _setup_gui(self):
        """Setup the main GUI components"""
        # Title
        title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 0))
        ctk.CTkLabel(title_frame, text=TITLE, 
                    font=ctk.CTkFont(*FONTS["title"])).pack()

        # Content area
        content = ctk.CTkFrame(self.root)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel (form)
        self._setup_form(content)
        
        # Right panel (SQL)
        self._setup_sql_panel(content)
        
        # Buttons
        self._setup_buttons()
        
        # Table
        self._setup_tables()

    def _setup_form(self, parent):
        """Setup the form panel"""
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(frame, text="Patient Information",
                    font=ctk.CTkFont(*FONTS["header"])).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create form fields
        for label_text, var_name in [
            ("Patient Number:", "patientNumber"),
            ("Patient Name:", "patientName"),
            ("Birth Date:", "birthDate"),
            ("Civil Status:", "civilStatus"),
            ("Occupation:", "occupation"),
            ("Religion:", "religion"),
            ("Education:", "education"),
            ("Illness Code:", "illnessCode"),
            ("Disease Name:", "diseaseName"),
            ("Detection Date:", "detectionDate"),
            ("Medicines Taken:", "medicinesTaken"),
            ("Past Surgery History:", "surgeryHistory"),
            ("Date of Surgery:", "surgeryDate"),
            ("Contact Person:", "contact"),
            ("Emergency Phone #:", "emergencyPhone"),
            ("Relationship:", "relationship")
        ]:
            row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(row, text=label_text, 
                        font=ctk.CTkFont(*FONTS["normal"]),
                        width=120, anchor="w").pack(side="left", padx=(10, 5))

            if var_name == "civilStatus":
                self._create_dropdown(row, var_name, MAPPINGS["civil_status"], "Single")
            elif var_name == "education":
                self._create_dropdown(row, var_name, MAPPINGS["education"], "None")
            else:
                UndoRedoEntry(row, textvariable=self.variables[var_name],
                           width=540, font=ctk.CTkFont(*FONTS["normal"])).pack(side="right")

    def _create_dropdown(self, parent, var_name, mapping, default):
        """Create a dropdown menu"""
        def on_select(choice):
            self.variables[var_name].set(mapping[choice])

        menu = ctk.CTkOptionMenu(
            parent,
            values=list(mapping.keys()),
            command=on_select,
            width=540,
            font=ctk.CTkFont(*FONTS["normal"])
        )
        menu.set(default)
        menu.pack(side="right")
        
        # Store reference to the dropdown
        self.dropdowns[var_name] = menu
        return menu

    def _setup_sql_panel(self, parent):
        """Setup the SQL query panel"""
        frame = ctk.CTkFrame(parent, width=700)
        frame.pack(side="right", fill="both", padx=(10, 0))
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text="SQL Query",
                    font=ctk.CTkFont(*FONTS["header"])).pack(pady=10)

        # Create a frame to hold both line numbers and text
        text_frame = ctk.CTkFrame(frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Use the same font for both text widgets
        text_font = ctk.CTkFont(*("CENTURY GOTHIC", 14))

        # Line numbers text widget
        self.line_numbers = ctk.CTkTextbox(
            text_frame,
            font=text_font,
            width=50,
            height=300
        )
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.configure(state="disabled")

        # Main SQL text widget with undo/redo enabled
        self.sql_text = ctk.CTkTextbox(
            text_frame,
            font=text_font,
            width=370,
            height=300
        )
        self.sql_text.pack(side="left", fill="both", expand=True)
        
        # Enable undo/redo on the underlying tkinter text widget
        self.sql_text._textbox.configure(undo=True, maxundo=-1)  # -1 means unlimited undo levels

        # Bind text changes to update line numbers
        self.sql_text.bind('<Key>', self._update_line_numbers)
        self.sql_text.bind('<MouseWheel>', self._sync_scroll)
        self.line_numbers.bind('<MouseWheel>', self._sync_scroll)

        # Bind font size changes
        self.sql_text.bind('<Control-plus>', lambda e: self._change_font_size(1))
        self.sql_text.bind('<Control-minus>', lambda e: self._change_font_size(-1))

        # Bind Ctrl+A for select all
        self.sql_text.bind('<Control-a>', self._select_all)

        # Store reference for global undo/redo handling
        self.text_widgets["sql"] = self.sql_text._textbox

        # Initial line numbers
        self._update_line_numbers()

    def _update_line_numbers(self, event=None):
        """Update the line numbers when text changes"""
        # Get the total number of lines
        final_index = self.sql_text.index("end-1c")
        num_of_lines = int(final_index.split(".")[0])

        # Enable editing of line numbers
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")

        # Create line numbers content
        line_numbers_text = "\n".join(str(i).rjust(3) for i in range(1, num_of_lines + 1))
        self.line_numbers.insert("1.0", line_numbers_text)

        # Disable editing of line numbers
        self.line_numbers.configure(state="disabled")

    def _sync_scroll(self, event):
        """Synchronize scrolling between main text and line numbers"""
        # Get the current view of the main text
        if event.widget == self.sql_text:
            self.line_numbers.yview_moveto(self.sql_text.yview()[0])
        else:
            self.sql_text.yview_moveto(self.line_numbers.yview()[0])
        return "break"  # Prevent default scrolling

    def _change_font_size(self, delta):
        """Change font size for both text widgets"""
        # Get current font properties
        current_font = self.sql_text.cget("font")
        current_size = int(current_font.cget("size"))

        # Calculate new size (minimum 8, maximum 72)
        new_size = max(8, min(72, current_size + delta))

        # Create new font
        new_font = ctk.CTkFont(*("CENTURY GOTHIC", new_size))

        # Apply to both widgets
        self.sql_text.configure(font=new_font)
        self.line_numbers.configure(font=new_font)

    def _select_all(self, event):
        """Select all text in the SQL text widget"""
        # Select all text
        self.sql_text.tag_add("sel", "1.0", "end-1c")
        
        # Set focus to the text widget
        self.sql_text.focus_set()
        
        # Prevent default behavior
        return "break"

    def _setup_buttons(self):
        """Setup action buttons"""
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(0, 20))

        # Action buttons
        commands = {
            "Insert Masterlist Data": self.save_data,
            "Add Disease": self.save_disease_masterlist,
            "Update": self.update_data,
            "Delete": self.delete_data,
            "Clear": self.clear_data,
            "Execute SQL Query": self.execute_sql_query
        }

        for text, color in BUTTONS.items():
            ctk.CTkButton(
                frame,
                text=text,
                command=commands[text],
                font=ctk.CTkFont(*FONTS["normal"]),
                width=120,
                fg_color=color
            ).pack(side="left" if text != "Execute SQL Query" else "right", padx=5)

    def _setup_tables(self):
        """Setup data tables"""
        frame = ctk.CTkFrame(self.root)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.table_notebook = ttk.Notebook(frame)
        self.table_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tables
        self.tables = {}
        for tab_name, columns in TABLE_STRUCTURES.items():
            if tab_name == "Credential" and not self.is_admin_view:
                continue  # Skip showing the Credential table in the GUI
            tab = ctk.CTkFrame(self.table_notebook)
            self.table_notebook.add(tab, text=tab_name)

            # Scrollbars
            scroll_x = ttk.Scrollbar(tab, orient="horizontal")
            scroll_y = ttk.Scrollbar(tab, orient="vertical")
            scroll_x.pack(side="bottom", fill="x")
            scroll_y.pack(side="right", fill="y")

            # Table
            style = ttk.Style()
            style.theme_use('default')
            treeview_style = THEME_CONFIG[self.current_theme]["treeview"]
            style.configure("Treeview", **treeview_style)
            style.configure("Treeview.Heading", **treeview_style)

            table = ttk.Treeview(
                tab,
                columns=columns,
                xscrollcommand=scroll_x.set,
                yscrollcommand=scroll_y.set,
                selectmode='extended'
            )

            scroll_x.config(command=table.xview)
            scroll_y.config(command=table.yview)

            for col in columns:
                table.heading(col, text=col.replace('_', ' ').title())
                table.column(col, width=120, anchor="center")

            table["show"] = "headings"
            table.pack(fill="both", expand=True)
            
            # Add Ctrl+A binding for selecting all rows
            def select_all_rows(event, tree=table):
                tree.selection_set(tree.get_children())
                return "break"  # Prevent default Ctrl+A behavior
            
            table.bind('<Control-a>', select_all_rows)
            table.bind('<Command-a>', select_all_rows)  # macOS
            
            self.tables[tab_name] = table

    def fetch_data(self):
        """Fetch and display data in tables"""
        try:
            for tab_name in TABLE_STRUCTURES:
                if tab_name == "Credential" and not self.is_admin_view:
                    continue  # Skip the Credential table in the GUI
                if tab_name not in self.tables:
                    continue  # Skip if table widget doesn't exist
                    
                table = self.tables[tab_name]
                table.delete(*table.get_children())
                
                data = self.db.fetch_data(tab_name.replace(" ", "_"))
                if data:
                    for row in data:
                        table.insert("", "end", values=row)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def save_data(self):
        """Save form data"""
        # Get data and strip whitespace from all string values
        data = {k: self.variables[k].get().strip() if isinstance(self.variables[k].get(), str) else self.variables[k].get() 
               for k in TABLE_STRUCTURES["Credential"]}
        
        if not self._validate_data(data):
            return

        try:
            # Split data for different tables using TABLE_STRUCTURES
            credential_data = {k: data[k] for k in TABLE_STRUCTURES["Credential"]}
            patient_profile_data = {k: data[k] for k in TABLE_STRUCTURES["Patient_Profile"]}
            medical_data = {k: data[k] for k in TABLE_STRUCTURES["Medical_History"]}
            surgery_data = {k: data[k] for k in TABLE_STRUCTURES["Surgery_History"] if k != "surgeryID"}

            if self.db.insert_normalized_data(credential_data, patient_profile_data, medical_data, surgery_data):
                self.fetch_data()
                self.clear_data()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def save_disease_masterlist(self):
        """Save disease masterlist entry"""
        data = {
            "diseaseName": self.variables["diseaseName"].get(),
            "illnessCode": self.variables["illnessCode"].get()
        }

        if not all(data.values()):
            messagebox.showerror("Error", "Disease Name and Illness Code are required")
            return

        try:
            if self.db.insert_disease_masterlist(data):
                self.fetch_data()
                self.variables["diseaseName"].set("")
                self.variables["illnessCode"].set("")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def update_data(self):
        """Update record based on Patient Number and Illness Code"""
        # Get the patient number and illness code
        patient_number = self.variables["patientNumber"].get()
        illness_code = self.variables["illnessCode"].get()

        # Validate required fields
        if not patient_number or not illness_code:
            messagebox.showerror("Error", "Patient Number and Illness Code are required for updating")
            return

        try:
            # Get current values from database
            current_data = self.db.get_current_values(patient_number, illness_code)
            if not current_data:
                messagebox.showerror("Error", "No record found with the given Patient Number and Illness Code")
                return

            # Create update data dictionary with only non-empty fields
            update_data = {}
            for field in TABLE_STRUCTURES["Credential"]:
                new_value = self.variables[field].get()
                if new_value:  # Only include non-empty fields
                    update_data[field] = new_value
                else:
                    # Keep the current value if new value is empty
                    update_data[field] = current_data.get(field, "")

            # Set conditions for update
            conditions = {
                "patientNumber": patient_number,
                "illnessCode": illness_code
            }

            # Perform the update
            if self.db.update_data("Credential", update_data, conditions):
                messagebox.showinfo("Success", "Record updated successfully")
                self.fetch_data()
                self.clear_data()
            else:
                messagebox.showerror("Error", "Failed to update record")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def delete_data(self):
        """Delete selected records"""
        current_tab = self.table_notebook.select()
        tab_name = self.table_notebook.tab(current_tab, "text")
        table = self.tables[tab_name]

        if not table.selection():
            messagebox.showwarning("Warning", "Please select records to delete")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "This will delete ALL data for the selected patient(s).\nAre you sure you want to continue?"
            if tab_name in ["Medical_History", "Surgery_History"]
            else "Are you sure you want to delete the selected records?"
        ):
            return

        try:
            records = []
            for item in table.selection():
                values = table.item(item)["values"]
                if tab_name == "Disease_Masterlist":
                    records.append(values[1])  # illnessCode
                else:
                    records.append(str(values[0]))  # patientNumber

            if tab_name == "Disease_Masterlist":
                if self.db.delete_from_disease_masterlist(records):
                    self.fetch_data()
            else:
                if self.db.batch_delete_records("Credential", records):
                    self.fetch_data()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def clear_data(self):
        """Clear form fields"""
        current_tab = self.table_notebook.select()
        tab_name = self.table_notebook.tab(current_tab, "text")

        if tab_name == "Disease_Masterlist":
            self.variables["diseaseName"].set("")
            self.variables["illnessCode"].set("")
        else:
            # Clear all text fields
            for var_name, var in self.variables.items():
                if var_name not in ["civilStatus", "education"]:
                    var.set("")

        # Reset dropdowns to their defaults
        self.dropdowns["civilStatus"].set("Single")
        self.dropdowns["education"].set("None")

    def execute_sql_query(self):
        """Execute custom SQL query"""
        query = self.sql_text.get("1.0", "end-1c").strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a SQL query")
            return

        try:
            results = self.db.execute_custom_query(query)
            
            # Create results window
            results_window = ctk.CTkToplevel()
            results_window.title("SQL Query Results")
            results_window.geometry("800x600")
            
            # Make the window stay on top and grab focus
            results_window.transient(self.root)  # Set as transient window of main window
            results_window.grab_set()  # Make the window modal
            
            if not results:
                # Show "No results found" message
                label = ctk.CTkLabel(
                    results_window,
                    text="No results found",
                    font=("Helvetica", 14)
                )
                label.pack(pady=20)
                return
            
            # Create table for results
            columns = [desc[0] for desc in self.db.cursor.description]
            table = ttk.Treeview(
                results_window,
                columns=columns,
                show="headings",
                selectmode='extended'
            )

            # Configure columns
            for col in columns:
                table.heading(col, text=col.replace('_', ' ').title())
                table.column(col, width=120, anchor="center")

            # Add scrollbars
            scroll_x = ttk.Scrollbar(results_window, orient="horizontal", command=table.xview)
            scroll_y = ttk.Scrollbar(results_window, orient="vertical", command=table.yview)
            table.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

            # Pack everything
            scroll_x.pack(side="bottom", fill="x")
            scroll_y.pack(side="right", fill="y")
            table.pack(fill="both", expand=True)

            # Insert data
            for row in results:
                table.insert("", "end", values=row)

            # Add Ctrl+A binding for selecting all rows
            def select_all(event):
                table.selection_set(table.get_children())
                return "break"  # Prevent default Ctrl+A behavior
            
            table.bind('<Control-a>', select_all)  # Windows/Linux
            table.bind('<Command-a>', select_all)  # macOS

            # Center the window on the screen
            results_window.update_idletasks()  # Update window size
            width = results_window.winfo_width()
            height = results_window.winfo_height()
            x = (results_window.winfo_screenwidth() // 2) - (width // 2)
            y = (results_window.winfo_screenheight() // 2) - (height // 2)
            results_window.geometry(f'{width}x{height}+{x}+{y}')
            
            # Add a protocol handler for the close button
            def on_closing():
                results_window.grab_release()  # Release the grab before destroying
                results_window.destroy()
            
            results_window.protocol("WM_DELETE_WINDOW", on_closing)

        except sqlite3.Error as e:
            messagebox.showerror("SQL Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _validate_data(self, data):
        """Validate form data"""
        try:
            # Required fields
            if not data["patientNumber"] or not data["patientName"]:
                messagebox.showerror("Error", "Patient Number and Name are required")
                return False

            # Patient Number (5 digits max)
            if not data["patientNumber"].isdigit() or len(data["patientNumber"]) > 5:
                messagebox.showerror("Error", "Patient Number must be up to 5 digits")
                return False

            # Field length validations
            limits = {
                "patientName": 150, "occupation": 60, "religion": 60,
                "medicinesTaken": 120, "surgeryHistory": 120, "diseaseName": 120,
                "contact": 60, "relationship": 60,
                "illnessCode": 30
            }

            for field, limit in limits.items():
                if len(data[field]) > limit:
                    messagebox.showerror("Error", 
                                       f"{field.title()} cannot exceed {limit} characters")
                    return False

            # Single-value date validation
            if data["birthDate"]:
                try:
                    if data["birthDate"].lower() == "n/a":
                        pass
                    else:
                        # Parse the date and convert to YYYY-MM-DD format
                        parsed_date = datetime.datetime.strptime(data["birthDate"], '%m/%d/%Y')
                        data["birthDate"] = parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    messagebox.showerror("Error", "Birth Date must be in MM/DD/YYYY format")
                    return False

            # Multi-valued date validations
            for field in ["detectionDate", "surgeryDate"]:
                if data[field]:
                    dates = [d.strip() for d in data[field].split(',')]
                    converted_dates = []
                    for date in dates:
                        try:
                            if date.lower() == "n/a":
                                converted_dates.append(date)
                            else:
                                # Parse and convert to YYYY-MM-DD format
                                parsed_date = datetime.datetime.strptime(date, '%m/%d/%Y')
                                converted_dates.append(parsed_date.strftime('%Y-%m-%d'))
                        except ValueError:
                            messagebox.showerror("Error", 
                                               f"Each {field.title()} must be in MM/DD/YYYY format")
                            return False
                    # Join the converted dates back into a comma-separated string
                    data[field] = ', '.join(converted_dates)

            # Phone number validation
            if len(data["emergencyPhone"]) > 14:
                messagebox.showerror("Error", 
                                   "Emergency Phone number cannot exceed 14 characters")
                return False

            return True

        except Exception as e:
            messagebox.showerror("Validation Error", str(e))
            return False

    def _drop_tables(self):
        """Drop all database tables after confirmation"""
        if not messagebox.askyesno(
            "Confirm Drop Tables",
            "WARNING: This will permanently delete ALL data from the database.\n\n"
            "Are you sure you want to drop all tables?"
        ):
            return

        try:
            # List of tables in order of dependencies
            drop_tables = [
                'Medical_History',
                'Surgery_History',
                'Patient_Profile',
                'Credential',
                'Disease_Masterlist'
            ]
            
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                for table in drop_tables:
                    cursor.execute(f'DROP TABLE IF EXISTS {table}')
                conn.commit()
            
            # Reinitialize the database tables
            self.db._setup_database()
            
            # Refresh the UI
            self.fetch_data()
            self.clear_data()
            
            messagebox.showinfo("Success", "All tables have been dropped and recreated successfully.")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to drop tables: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernHospital()
    app.run() 