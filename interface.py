import os
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from datetime import datetime
import tkinter.font as tkfont
from PIL import Image, ImageTk



from behavior_model import BehaviorModel
from infection_rules import InfectionRules
from simulation import Simulation
from membrane import Membrane


@dataclass
class SimulationParameters:
    """Data class to hold all simulation parameters for the simulation."""

    # Basic Parameters
    TOTAL_POPULATION: int
    INIT_INFECTIONS_PER_PROVINCE: int
    SIMULATION_DAYS: int
    NUM_OF_PROV: int

    # Infection Rules Parameters
    INCUBATION_PERIOD: int
    CAUTION_FACTOR: float
    PRUDENCE_PARAMETER: float
    BEHAVIOR_TRIGGER: bool
    VACCINATION_TRIGGER: bool
    VIRAL_LOAD: bool
    ICU_PRESENCE: bool

    # Behavior Model Parameters
    VACCINE_COVERAGE: float
    DURATION_CORRELATION: float
    F_STAR: float

    # Restriction Parameters
    QUARANTINE_ENABLED: bool
    QUARANTINE_DURATION: int
    QUARANTINE_START_DAY: int

    @classmethod
    def from_dict(cls, param_dict):
        """Factory method to create a SimulationParameters instance from a dictionary."""
        return cls(
            # Basic Parameters
            TOTAL_POPULATION=int(param_dict['TOTAL_POPULATION']),
            INIT_INFECTIONS_PER_PROVINCE=int(param_dict['INIT_INFECTIONS_PER_PROVINCE']),
            SIMULATION_DAYS=int(param_dict['SIMULATION_DAYS']),
            NUM_OF_PROV=int(param_dict['NUM_OF_PROV']),

            # Infection Rules Parameters
            INCUBATION_PERIOD=int(param_dict['INCUBATION_PERIOD']),
            CAUTION_FACTOR=float(param_dict['CAUTION_FACTOR']),
            PRUDENCE_PARAMETER=float(param_dict['PRUDENCE_PARAMETER']),
            BEHAVIOR_TRIGGER=param_dict['BEHAVIOR_TRIGGER'] == '1',
            VACCINATION_TRIGGER=param_dict['VACCINATION_TRIGGER'] == '1',
            VIRAL_LOAD=param_dict['VIRAL_LOAD'] == '1',
            ICU_PRESENCE=param_dict['ICU_PRESENCE'] == '1',

            # Behavior Model Parameters
            VACCINE_COVERAGE=float(param_dict['VACCINE_COVERAGE']),
            DURATION_CORRELATION=float(param_dict['DURATION_CORRELATION']),
            F_STAR=float(param_dict['F_STAR']),

            # Restriction Parameters
            QUARANTINE_ENABLED=param_dict['QUARANTINE_ENABLED'] == '1',
            QUARANTINE_DURATION=int(param_dict['QUARANTINE_DURATION']),
            QUARANTINE_START_DAY=int(param_dict['QUARANTINE_START_DAY']),
        )

    def to_dict(self):
        """Convert the parameters to a dictionary format."""
        return {
            # Basic Parameters
            'TOTAL_POPULATION': self.TOTAL_POPULATION,
            'INIT_INFECTIONS_PER_PROVINCE': self.INIT_INFECTIONS_PER_PROVINCE,
            'SIMULATION_DAYS': self.SIMULATION_DAYS,
            'NUM_OF_PROV': self.NUM_OF_PROV,

            # Infection Rules Parameters
            'INCUBATION_PERIOD': self.INCUBATION_PERIOD,
            'CAUTION_FACTOR': self.CAUTION_FACTOR,
            'PRUDENCE_PARAMETER': self.PRUDENCE_PARAMETER,
            'BEHAVIOR_TRIGGER': '1' if self.BEHAVIOR_TRIGGER else '0',
            'VACCINATION_TRIGGER': '1' if self.VACCINATION_TRIGGER else '0',
            'VIRAL_LOAD': '1' if self.VIRAL_LOAD else '0',
            'ICU_PRESENCE': '1' if self.ICU_PRESENCE else '0',

            # Behavior Model Parameters
            'VACCINE_COVERAGE': self.VACCINE_COVERAGE,
            'DURATION_CORRELATION': self.DURATION_CORRELATION,
            'F_STAR': self.F_STAR,

            # Restriction Parameters
            'QUARANTINE_ENABLED': '1' if self.QUARANTINE_ENABLED else '0',
            'QUARANTINE_DURATION': self.QUARANTINE_DURATION,
            'QUARANTINE_START_DAY': self.QUARANTINE_START_DAY,
        }


class ToolTip:
    """Creates interactive tooltips for GUI elements to provide additional information."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Display the tooltip when mouse hovers over the widget."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create a toplevel window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        # Enhanced tooltip styling with gradient background
        frame = ttk.Frame(self.tooltip, borderwidth=1, relief="solid")
        frame.pack(fill="both", expand=True)

        label = ttk.Label(frame, text=self.text, justify='left',
                          background="#F0F8FF", wraplength=300,
                          font=('Segoe UI', 10))
        label.pack(padx=8, pady=8)

    def hide_tooltip(self, event=None):
        """Remove the tooltip when mouse leaves the widget."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class SimulationGUI:
    """Main GUI class for the epidemic simulation interface."""
    def __init__(self, root):
        """Initialize the GUI with all necessary components and styling."""
        self.root = root
        self.root.title("Epidemic Simulation Interface")

        # Set window size
        self.root.geometry("650x750")
        self.root.minsize(650, 750)

        # Apply a modern theme and custom color scheme
        self.setup_theme()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=15, pady=10)

        # Create tabs
        self.basic_tab = ttk.Frame(self.notebook)
        self.infection_tab = ttk.Frame(self.notebook)
        self.behavior_tab = ttk.Frame(self.notebook)
        self.restrictions_tab = ttk.Frame(self.notebook)
        self.graph_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook
        self.notebook.add(self.basic_tab, text='Basic Parameters')
        self.notebook.add(self.infection_tab, text='Infection Rules')
        self.notebook.add(self.behavior_tab, text='Behavior Model')
        self.notebook.add(self.restrictions_tab, text='Restrictions')
        self.notebook.add(self.graph_tab, text='Simulation Output')

        # Parameter descriptions
        self.parameter_info = {
            'TOTAL_POPULATION': 'Total number of individuals in the simulation. Suggested values range from 500 to 30000',
            'INIT_INFECTIONS_PER_PROVINCE': 'Number of initially infected individuals in each province.',
            'SIMULATION_DAYS': 'Total duration of the simulation in days. Its suggested to not go over 365 days',
            'NUM_OF_PROV': 'Number of provinces in the simulation.Suggested value range from 2-12. The higher the population the higher the number of provinces',
            'INCUBATION_PERIOD': 'This parameter has effect only if the viral load parameter is off. Indicates the number of days before symptoms appear in infected individuals.',
            'CAUTION_FACTOR': 'The Caution Factor determines how quickly people adopt cautious behavior as infections rise; a higher value means the population is less cautious. (0-1).',
            'PRUDENCE_PARAMETER': 'The Prudence Parameter (PP) represents how cautious symptomatic individuals are about staying home; a higher value means they are more likely to self-isolate, reducing the spread of infection. (0-1).',
            'BEHAVIOR_TRIGGER': 'When enabled, enables the use of caution factor in the simulation.',
            'VACCINATION_TRIGGER': 'When enabled, vaccination status affects transmission probability.',
            'VIRAL_LOAD': 'When enabled, uses "LOIMOS" based infection system, (more realistic and reliable). When disabled, uses "MVT" based infection system(faster). Read the documentation to understand more about this.',
            'ICU_PRESENCE': 'When enabled, includes ICU membrane in the model.',
            'VACCINE_COVERAGE': 'Percentage of population that is vaccinated from the start of the simulation (0-1).',
            'DURATION_CORRELATION': 'Controls how strongly the vaccine effectiveness is linked to how long it lasts. The higher it is, the more effective and lasting is the vaccine.  (0-1).',
            'F_STAR': 'A reference point that helps determine how people’s willingness to get vaccinated changes based on infection levels. The higher it is, the less willing people are to get vaccinated.(0-1. 0.001 to 0.1 are the suggested values)',
            'QUARANTINE_ENABLED': 'When enabled, quarantine measures are implemented.',
            'QUARANTINE_DURATION': 'Length of quarantine period in days.',
            'QUARANTINE_START_DAY': 'Day when quarantine measures begin.'
        }

        # Dictionary to store variables
        self.variables = {}

        # Create content for each tab and for buttons
        self.create_basic_tab()
        self.create_infection_tab()
        self.create_behavior_tab()
        self.create_restrictions_tab()
        self.create_graph_tab()
        self.create_output_section()
        self.create_control_buttons()

    def setup_theme(self):
        """Configure custom theme and styles for modern appearance."""
        style = ttk.Style()

        # Use a modern base theme if available
        if 'alt' in style.theme_names():
            style.theme_use('alt')

        # Define custom colors
        bg_color = '#f5f7fa'
        accent_color = '#3498db'
        accent_hover = '#2980b9'
        text_color = '#2c3e50'
        header_color = '#34495e'

        # Apply custom background
        self.root.configure(background=bg_color)

        # Notebook styling (tabs)
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', padding=(15, 8), font=('Segoe UI', 11), foreground=text_color)
        style.map('TNotebook.Tab',
                  foreground=[('selected', accent_color)],
                  background=[('selected', bg_color)])

        # Frame styling
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, borderwidth=1)
        style.configure('TLabelframe.Label', font=('Segoe UI', 12, 'bold'), foreground=header_color)

        # Button styling
        style.configure('TButton', font=('Segoe UI', 11), padding=(10, 6), background=bg_color)

        # Run button with accent color
        style.configure('Run.TButton', font=('Segoe UI', 12, 'bold'), padding=(20, 10),
                        background=accent_color, foreground='white')
        style.map('Run.TButton',
                  background=[('active', accent_hover)],
                  foreground=[('active', 'white')])

        # Clear button with more subtle styling
        style.configure('Clear.TButton', font=('Segoe UI', 12), padding=(20, 10))

        # Label and input styling
        style.configure('TLabel', font=('Segoe UI', 11), background=bg_color, foreground=text_color)
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), background=bg_color, foreground=header_color)
        style.configure('TEntry', font=('Segoe UI', 11), padding=8)
        style.configure('TCheckbutton', font=('Segoe UI', 11), background=bg_color)

        # Info button styling
        style.configure('Info.TLabel', font=('Segoe UI', 10, 'bold'), foreground=accent_color)

        # Setting up custom scrollbar style
        style.layout('Vertical.TScrollbar',
                     [('Vertical.Scrollbar.trough',
                       {'children': [('Vertical.Scrollbar.thumb',
                                      {'expand': '1', 'sticky': 'nswe'})],
                        'sticky': 'ns'})])
        style.configure('Vertical.TScrollbar', background=accent_color, borderwidth=0, arrowsize=16)
        style.map('Vertical.TScrollbar', background=[('active', accent_hover)])

    def create_header(self):
        """Create header with application title and description."""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=20, pady=(15, 5))

        title_label = ttk.Label(header_frame, text="Epidemic Simulation Model",
                                style='Header.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 5))

        desc_label = ttk.Label(header_frame,
                               text="Configure parameters to simulate disease spread and intervention strategies",
                               wraplength=700)
        desc_label.pack(pady=(0, 10))

    def create_basic_tab(self):
        """Create basic parameters tab content"""
        frame = ttk.LabelFrame(self.basic_tab, text="Basic Simulation Parameters")
        frame.pack(fill='x', padx=15, pady=10, ipady=5)

        params = {
            'TOTAL_POPULATION': ('Total Population:', Simulation.TOTAL_POPULATION),
            'INIT_INFECTIONS_PER_PROVINCE': ('Initial Infections per Province:', Simulation.INIT_INFECTIONS_PER_PROVINCE),
            'SIMULATION_DAYS': ('Simulation Days:', 10),
            'NUM_OF_PROV': ('Number of Provinces:', 12)
        }

        for i, (param_name, (label_text, default_value)) in enumerate(params.items()):
            self.add_input_field(frame, param_name, label_text, i, default_value)

    def create_infection_tab(self):
        """Create infection rules tab content"""
        frame = ttk.LabelFrame(self.infection_tab, text="Infection Parameters")
        frame.pack(fill='x', padx=15, pady=10, ipady=5)

        row = 0
        # Numerical parameters
        params = {
            'INCUBATION_PERIOD': ('Incubation Period:', InfectionRules.INCUBATION_PERIOD),
            'CAUTION_FACTOR': ('Caution Factor:', InfectionRules.CAUTION_FACTOR),
            'PRUDENCE_PARAMETER': ('Prudence Parameter:', InfectionRules.PRUDENCE_PARAMETER)
        }

        for param_name, (label_text, default_value) in params.items():
            self.add_input_field(frame, param_name, label_text, row, default_value)
            row += 1

        # Checkboxes
        self.add_checkbox(frame, 'BEHAVIOR_TRIGGER', 'Behavior Trigger:', row, InfectionRules.BEHAVIOR_TRIGGER)
        row += 1
        self.add_checkbox(frame, 'VACCINATION_TRIGGER', 'Vaccination Trigger:', row, InfectionRules.VACCINATION_TRIGGER)
        row += 1
        self.add_checkbox(frame, 'VIRAL_LOAD', 'Viral Load:', row, InfectionRules.VIRAL_LOAD)
        row += 1
        self.add_checkbox(frame, 'ICU_PRESENCE', 'ICU Presence:', row, InfectionRules.ICU_PRESENCE)

    def create_behavior_tab(self):
        """Create behavior model tab content"""
        frame = ttk.LabelFrame(self.behavior_tab, text="Behavior Model Parameters")
        frame.pack(fill='x', padx=15, pady=10, ipady=5)

        params = {
            'VACCINE_COVERAGE': ('Vaccine Coverage:', Simulation.VACCINE_COVERAGE),
            'DURATION_CORRELATION': ('Duration Correlation:', BehaviorModel.DURATION_CORRELATION),
            'F_STAR': ('F Star:', BehaviorModel.F_STAR)
        }

        for i, (param_name, (label_text, default_value)) in enumerate(params.items()):
            self.add_input_field(frame, param_name, label_text, i, default_value)

    def create_restrictions_tab(self):
        """Create restrictions tab content"""
        frame = ttk.LabelFrame(self.restrictions_tab, text="Restriction Parameters")
        frame.pack(fill='x', padx=15, pady=10, ipady=5)

        row = 0
        # Quarantine parameters
        self.add_checkbox(frame, 'QUARANTINE_ENABLED', 'Enable Quarantine:', row, False)
        row += 1
        self.add_input_field(frame, 'QUARANTINE_DURATION', 'Quarantine Duration (days):', row, 14)
        row += 1
        self.add_input_field(frame, 'QUARANTINE_START_DAY', 'Quarantine Start Day:', row, 7)

    def create_graph_tab(self):
        """Create graph display tab content"""
        # Main frame for the graph tab
        self.graph_frame = ttk.Frame(self.graph_tab)
        self.graph_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Initial message
        self.graph_message = ttk.Label(
            self.graph_frame,
            text="Run a simulation to view output graphs here.",
            font=('Segoe UI', 12)
        )
        self.graph_message.pack(pady=50)

        # Create a frame to hold the graph images - will be populated after simulation
        self.graphs_container = ttk.Frame(self.graph_frame)
        self.graphs_container.pack(fill='both', expand=True)

        # Define placeholder for graph image labels
        self.graph_images = []
        self.graph_photo_refs = []  # Keep references to prevent garbage collection

    def add_input_field(self, parent, var_name, label_text, row, default_value):
        """Add a labeled input field with info button"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5, padx=10)

        # Label for parameter
        label = ttk.Label(frame, text=label_text, width=25)
        label.pack(side='left', padx=5)

        # Entry field
        self.variables[var_name] = tk.StringVar(value=str(default_value))
        entry = ttk.Entry(frame, textvariable=self.variables[var_name], width=15)
        entry.pack(side='left', padx=5)

        # Info button
        info_btn = ttk.Label(frame, text="i", style='Info.TLabel', cursor="hand2")
        info_btn.pack(side='left', padx=5)

        # Create tooltip for info button
        ToolTip(info_btn, self.parameter_info.get(var_name, "No description available"))

    def display_simulation_graphs(self, csv_filename):
        """Display the graphs generated from the simulation and clean up temporary files"""
        # Clear any existing content
        for widget in self.graphs_container.winfo_children():
            widget.destroy()
        self.graph_images = []
        self.graph_photo_refs = []

        # Hide the initial message
        self.graph_message.pack_forget()

        # Get the simulation timestamp from the CSV filename
        # Format is "simulation_results___YYYYMMDD_HHMMSS.csv"
        timestamp = os.path.basename(csv_filename).split("___")[1].replace(".csv", "")

        # Get the graph directory based on the CSV filename
        graph_dir = os.path.join(os.path.dirname(csv_filename), "graphs")

        if not os.path.exists(graph_dir):
            ttk.Label(
                self.graphs_container,
                text="No graphs found. Please run the simulation again.",
                font=('Segoe UI', 11)
            ).pack(pady=20)
            return

        # Create scrollable frame for graphs
        canvas = tk.Canvas(self.graphs_container)
        scrollbar = ttk.Scrollbar(self.graphs_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Calculate desired width for the graphs (slightly smaller than tab width)
        graph_width = 580  # Adjust as needed

        # Find all PNG files in the graph directory that match the current simulation timestamp
        graph_files = [f for f in os.listdir(graph_dir) if f.endswith('.png') and timestamp in f]

        if not graph_files:
            ttk.Label(
                scrollable_frame,
                text="No graphs found for the current simulation.",
                font=('Segoe UI', 11)
            ).pack(pady=20)
            return

        # Sort graph files to ensure consistent order
        graph_files.sort()

        # Load and display each graph
        for i, graph_file in enumerate(graph_files):
            graph_path = os.path.join(graph_dir, graph_file)

            # Create a label for the graph title
            # Remove timestamp from the display title for cleaner presentation
            title = graph_file.split("___")[0].replace('_', ' ')
            title_label = ttk.Label(
                scrollable_frame,
                text=title,
                font=('Segoe UI', 11, 'bold')
            )
            title_label.pack(pady=(20 if i > 0 else 10, 5))

            try:
                # Open and resize the image to fit the width
                img = Image.open(graph_path)
                # Calculate height to maintain aspect ratio
                wpercent = (graph_width / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((graph_width, hsize), Image.LANCZOS)

                # Convert to PhotoImage and keep a reference
                photo = ImageTk.PhotoImage(img)
                self.graph_photo_refs.append(photo)  # Keep reference to prevent garbage collection

                # Create and pack image label
                img_label = ttk.Label(scrollable_frame, image=photo)
                img_label.pack(pady=5)
                self.graph_images.append(img_label)

            except Exception as e:
                error_label = ttk.Label(
                    scrollable_frame,
                    text=f"Error loading graph: {str(e)}",
                    foreground="red"
                )
                error_label.pack(pady=5)

        # All graphs loaded successfully, now we can remove the CSV file
        try:
            if os.path.exists(csv_filename):
                os.remove(csv_filename)
                print(f"Cleaned up temporary CSV file: {csv_filename}")
        except Exception as e:
            print(f"Warning: Could not remove CSV file: {e}")

        # Switch to the graph tab to show the results
        self.notebook.select(self.graph_tab)

    def add_checkbox(self, parent, var_name, label_text, row, default_value):
        """Add a labeled checkbox with info button"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5, padx=10)

        # Label for parameter
        label = ttk.Label(frame, text=label_text, width=25)
        label.pack(side='left', padx=5)

        # Checkbox
        self.variables[var_name] = tk.StringVar(value='1' if default_value else '0')
        checkbox = ttk.Checkbutton(frame, variable=self.variables[var_name], onvalue='1', offvalue='0')
        checkbox.pack(side='left', padx=5)

        # Info button
        info_btn = ttk.Label(frame, text="i", style='Info.TLabel', cursor="hand2")
        info_btn.pack(side='left', padx=5)

        # Create tooltip for info button
        ToolTip(info_btn, self.parameter_info.get(var_name, "No description available"))

    def create_control_buttons(self):
        """Create control buttons with improved styling"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        run_btn = ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation, style='Run.TButton')
        run_btn.pack(side=tk.LEFT, padx=10)

        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_fields)
        clear_btn.pack(side=tk.LEFT, padx=10)

    def create_output_section(self):
        """Create output section with improved styling"""
        output_frame = ttk.LabelFrame(self.root, text="Simulation Results")
        output_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Use a monospace font for better alignment of data
        output_font = tkfont.Font(family="Consolas", size=10)
        self.output_text = tk.Text(output_frame, height=15, font=output_font)
        self.output_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scrollbar.pack(side='right', fill='y', pady=5)
        self.output_text.configure(yscrollcommand=scrollbar.set)

    def run_simulation(self):
        """Execute the simulation with the current parameter values."""
        try:
            # Clear previous output
            self.output_text.delete(1.0, tk.END)

            # Get parameters from GUI
            params = self.get_parameters()

            # Initialize simulation instance with parameters
            simulation = Simulation()
            Simulation.update_total_population(params.TOTAL_POPULATION)
            Simulation.update_initial_infection_per_province(params.INIT_INFECTIONS_PER_PROVINCE)
            Simulation.update_vaccine_coverage(params.VACCINE_COVERAGE)

            Simulation.update_quarantine_enabled(params.QUARANTINE_ENABLED)
            Simulation.update_quarantine_duration(params.QUARANTINE_DURATION)
            Simulation.update_quarantine_start_day(params.QUARANTINE_START_DAY)

            # Initialize behavior model with parameters
            behavior_model = BehaviorModel()
            BehaviorModel.update_duration_correlation(params.DURATION_CORRELATION)
            BehaviorModel.update_f_star(params.F_STAR)

            # Initialize infection rules with parameters
            infection_rules = InfectionRules()
            InfectionRules.update_incubation_period(params.INCUBATION_PERIOD)
            InfectionRules.update_caution_factor(params.CAUTION_FACTOR)
            InfectionRules.update_prudence_parameter(params.PRUDENCE_PARAMETER)
            InfectionRules.update_behavior_trigger(params.BEHAVIOR_TRIGGER)
            InfectionRules.update_vaccine_trigger(params.VACCINATION_TRIGGER)
            InfectionRules.update_viral_load(params.VIRAL_LOAD)
            InfectionRules.update_ICU_presence(params.ICU_PRESENCE)

            # Initialize membrane with parameters
            mem = Membrane('PV')
            Membrane.update_num_of_prov(params.NUM_OF_PROV)

            # Set the models in the simulation
            simulation.behavior_model = behavior_model
            simulation.infection_rules = infection_rules
            simulation.mem = mem

            # Save simulation parameters
            os.makedirs("simulations", exist_ok=True)
            simulation_params = params.to_dict()

            current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"simulations/simulation_parameters___{current_datetime}.txt"

            # Define the CSV output filename for use in both saving and graph display
            csv_filename = f"simulations/simulation_results___{current_datetime}.csv"

            with open(output_file, 'w') as file:
                file.write("Simulation Parameters:\n")
                for key, value in simulation_params.items():
                    file.write(f"{key}: {value}\n")

            # Initialize the simulation scenario
            simulation.create_scenario()

            # Add headers to output
            self.output_text.insert(tk.END, f"{'Day':<6}{'New Cases':<12}{'Prevalence':<12}{'Deaths':<8}{'Seconds':<8}\n")
            self.output_text.insert(tk.END, "-" * 50 + "\n")
            self.output_text.update()

            # Update output with simulation progress
            def update_simulation_output(day, new_cases, prevalence, deaths, seconds):
                if day == "ALERT":
                    # Directly insert the alert text without numerical formatting
                    output_line = f"\n{new_cases}\n\n"
                else:
                    # Standard daily stats row
                    # We use a try/except block to handle the 'seconds' formatting safely
                    try:
                        # Ensure seconds is treated as a float for the :.2f formatter
                        val_seconds = float(seconds) if seconds != "" else 0.0
                        output_line = f"{day:<6}{new_cases:<12}{prevalence:<12}{deaths:<8}{val_seconds:<8.2f}\n"
                    except (ValueError, TypeError):
                        # Fallback if formatting fails
                        output_line = f"{day:<6}{new_cases:<12}{prevalence:<12}{deaths:<8}{seconds:<8}\n"

                self.output_text.insert(tk.END, output_line)
                self.output_text.see(tk.END) # Scroll to the bottom
                self.output_text.update()

            # Connect to simulation results
            simulation.on_day_completed = update_simulation_output

            # Run the simulation
            simulation.run_simulation(days=params.SIMULATION_DAYS)

            # Add final summary
            self.output_text.insert(tk.END, "\nSimulation completed!\n")
            self.output_text.see(tk.END)

            # Display the simulation graphs
            self.display_simulation_graphs(csv_filename)

             # Switch to the graph tab to show the results
            self.notebook.select(self.graph_tab)

        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numerical values for all fields: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def clear_fields(self):
        """Reset all input fields and output text"""
        for var in self.variables.values():
            var.set("")
        self.output_text.delete(1.0, tk.END)

    def get_parameters(self) -> SimulationParameters:
        """Collect all parameters from the GUI"""
        param_dict = {name: var.get() for name, var in self.variables.items()}
        return SimulationParameters.from_dict(param_dict)


def main():
    """Main entry point for the application"""
    def center_window(window, width, height):
        """Center the window on screen"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2 - 40
        window.geometry(f"{width}x{height}+{x}+{y}")

    # Create the root window
    root = tk.Tk()
    root.configure(background="#f0f0f0")

    # Create the GUI
    SimulationGUI(root)
    center_window(root, 650, 750)

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()