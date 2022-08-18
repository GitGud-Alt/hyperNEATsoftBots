import numpy as np
from lxml import etree
from copy import deepcopy

class VXA:
    """Class representing a .vxa file."""
    
    def __init__(self, src:str=None, HeapSize=0.25, DtFrac=0.95, BondDampingZ=1.0, ColDampingZ=0.8, SlowDampingZ=0.01, 
                 SimTime=0.5, RecordStepSize=0.0, RecordVoxel=1.0, RecordFixedVoxels=1.0, RecordLink=0.0, 
                 EnableCollision=1.0, EnableExpansion=1.0, EnableSignals=0.0, EnableCilia=0.0, GravEnabled=1.0, GravAcc=-9.81, FloorEnabled=1.0, 
                 TempEnabled=1.0, TempBase=25.0, VaryTempEnabled=1.0, TempAmplitude=20.0, TempPeriod=0.1, Lattice_Dim=0.01):
        """Creates an XML tree with provided arguments. \n
        If src is provided, that file is parsed and any additional arguments overwrite the corresponding file values.

        Args:
            src (str, optional): Relative path for pre-existing .vxa file. Defaults to None.
            HeapSize (float, optional): Proportion of GPU memory to use for heap. Defaults to 0.25.
            DtFrac (float, optional): Restrict maximum timestep length. Defaults to 0.95.
            BondDampingZ (float, optional): Voxel vibration scale, 0 is none and 1 is max. Defaults to 1.0.
            ColDampingZ (float, optional): Voxel bouncing scale, 0 is none and 1 is max. Defaults to 0.8.
            SlowDampingZ (float, optional): Voxel phyics dampening, 0 is none and 1 is max. Defaults to 0.01.
            SimTime (float, optional): Simulation duration in seconds. Defaults to 0.5.
            RecordStepSize (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            RecordVoxel (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            RecordFixedVoxels (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            RecordLink (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            EnableCollision (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            EnableExpansion (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            EnableSignals (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            EnableCilia (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            GravEnabled (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            GravAcc (float, optional): Gravitational force. Defaults to -9.81.
            FloorEnabled (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            TempEnabled (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            TempBase (float, optional): Base level of global temperature. Defaults to 25.0.
            VaryTempEnabled (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            TempAmplitude (float, optional): Amplitude of temperature oscillation. Defaults to 20.0.
            TempPeriod (float, optional): Period of temperature oscillation. Defaults to 0.1.
            Lattice_Dim (float, optional): Voxel dimensions. Defaults to 0.01.
            
        Raises:
            SyntaxError: Indicates that provided .vxa file has missing tags.

        Returns:
            (VXA): VXA object with the specified arguments.
        """

        args = deepcopy(locals())
        defs = dict(zip(reversed(list(args.keys())[:-2]), VXA.__init__.__defaults__[1:]))

        self.root = None

        # Load VXA from file
        if src != None:
            parser = etree.XMLParser(remove_blank_text=True)
            self.root = etree.parse(src, parser).getroot()
        # Create VXA from scratch
        else:
            # = VXA = 
            self.root = etree.XML("<VXA></VXA>")
            self.root.set('Version', '1.1')

            # == GPU ==
            gpu = etree.SubElement(self.root, 'GPU')
            etree.SubElement(gpu, "HeapSize").text = str(HeapSize)
            
            # == Simulator ==
            simulator = etree.SubElement(self.root, "Simulator")
            etree.SubElement(simulator, "EnableCilia").text = str(EnableCilia)
            etree.SubElement(simulator, "EnableSignals").text = str(EnableSignals)
            etree.SubElement(simulator, "EnableExpansion").text = str(EnableExpansion) # 0 only contraction, 1 is contraction + expansion
            etree.SubElement(simulator, "MaxDistInVoxelLengthsToCountAsPair").text = "2"
            # === Integration ===
            integration = etree.SubElement(simulator, "Integration")
            etree.SubElement(integration, "DtFrac").text = str(DtFrac)
            # === Damping ===
            damping = etree.SubElement(simulator, "Damping")
            etree.SubElement(damping, "BondDampingZ").text = str(BondDampingZ)
            etree.SubElement(damping, "ColDampingZ").text = str(ColDampingZ)
            etree.SubElement(damping, "SlowDampingZ").text = str(SlowDampingZ)
            # === AttachDetach ===
            attachDetach = etree.SubElement(simulator, "AttachDetach")
            etree.SubElement(attachDetach, "EnableCollision").text = str(EnableCollision)
            # === StopCondition ===
            stopCondition = etree.SubElement(simulator, "StopCondition")
            formula = etree.SubElement(stopCondition, "StopConditionFormula")
            sub = etree.SubElement(formula, "mtSUB")
            etree.SubElement(sub, "mtVAR").text = 't'
            etree.SubElement(sub, "mtCONST").text = str(SimTime)
            # === Fitness Function ===
            fitness = etree.SubElement(simulator, "FitnessFunction")
            # ==== (Euclidian Distance) ====
            abs_1 = etree.SubElement(fitness, "mtABS")
            add_1 = etree.SubElement(abs_1, "mtADD")
            mul_l = etree.SubElement(add_1, 'mtMUL')
            etree.SubElement(mul_l, "mtVAR").text = 'x'
            etree.SubElement(mul_l, "mtVAR").text = 'x'
            mul_2 = etree.SubElement(add_1, 'mtMUL')
            etree.SubElement(mul_2, "mtVAR").text = 'y'
            etree.SubElement(mul_2, "mtVAR").text = 'y'
            mul_3 = etree.SubElement(add_1, 'mtMUL')
            etree.SubElement(mul_3, "mtVAR").text = 'z'
            etree.SubElement(mul_3, "mtVAR").text = 'z'

            # === RecordHistory ===
            history = etree.SubElement(simulator, "RecordHistory")
            etree.SubElement(history, "RecordStepSize").text = str(RecordStepSize) #Capture image every 100 time steps
            etree.SubElement(history, "RecordVoxel").text = str(RecordVoxel) # Add voxels to the visualization
            etree.SubElement(history, "RecordLink").text = str(RecordLink) # Add links to the visualization
            etree.SubElement(history, "RecordFixedVoxels").text = str(RecordFixedVoxels) 
            
            # == Environment ==
            environment = etree.SubElement(self.root, "Environment")
            thermal = etree.SubElement(environment, "Thermal")
            etree.SubElement(thermal, "TempEnabled").text = str(TempEnabled)
            etree.SubElement(thermal, "VaryTempEnabled").text = str(VaryTempEnabled)
            etree.SubElement(thermal, "TempPeriod").text = str(TempPeriod)
            etree.SubElement(thermal, "TempAmplitude").text = str(TempAmplitude)
            etree.SubElement(thermal, "TempBase").text = str(TempBase)
            # === Gravity ===
            gravity = etree.SubElement(environment, "Gravity")
            etree.SubElement(gravity, "GravEnabled").text = str(GravEnabled)
            etree.SubElement(gravity, "GravAcc").text = str(GravAcc)
            etree.SubElement(gravity, "FloorEnabled").text = str(FloorEnabled)

            # == VXC ==
            vxc = etree.SubElement(self.root, "VXC")
            vxc.set("Version", "0.94")
            # === Lattice ===
            lattice = etree.SubElement(vxc, "Lattice")
            etree.SubElement(lattice, "Lattice_Dim").text = str(Lattice_Dim)
            # === Voxel ===
            voxel = etree.SubElement(vxc, "Voxel")
            etree.SubElement(lattice, "Vox_Name").text = str("BOX")
            etree.SubElement(lattice, "X_Squeeze").text = str(1.0)
            etree.SubElement(lattice, "Y_Squeeze").text = str(1.0)
            etree.SubElement(lattice, "Z_Squeeze").text = str(1.0)
            # === Palette ===
            palette = etree.SubElement(vxc, "Palette")
            # === Structure ===
            structure = etree.SubElement(vxc, "Structure")
            structure.set('Compression', 'ASCII_READABLE')

        # Overwrite VXA with provided arguments (if given)
        for k in defs.keys():
            if (str(args[k]) != str(defs[k])):
                elem = self.root.find(".//" + str(k))
                if (k == "SimTime"):
                    # Edge case
                    elem = self.root.find(".//mtCONST")
                elif (elem == None):
                    raise SyntaxError("ERROR: Could not find "+ str(k) +" tag in .vxa file")
                
                elem.text = str(args[k])


    def get_voxelspace(self):
        """Returns pre-defined voxel space as 3D array, as well as pre-defined origin
        point for placing organisms.

        Returns:
            (np.array): 3D array describing voxel space.
            (tuple): Vector for origin point within voxel space.
        """

        structure = self.root.find("*/Structure")
        # No structure
        if (len(list(structure.iter())) < 8):
            return np.empty(shape=(0, 0, 0)), (0, 0, 0)

        # Dimensions
        x_dim = int(float(structure.find("X_Voxels").text))
        y_dim = int(float(structure.find("Y_Voxels").text))
        z_dim = int(float(structure.find("Z_Voxels").text))
        env_arr = np.zeros(shape=(x_dim, y_dim, z_dim))
        # Origin
        x_org = int(float(structure.find("X_OSpawn").text))
        y_org = int(float(structure.find("Y_OSpawn").text))
        z_org = int(float(structure.find("Z_OSpawn").text))
        org_arr = (x_org, y_org, z_org)

        for z, layer in enumerate(structure.find("Data").findall("Layer")):
            for xy, value in enumerate(layer.text):
                x = int(xy % (x_dim))
                y = int((xy - x) / (x_dim))
                env_arr[x, y, z] = int(value)

        return env_arr, org_arr

    def add_material(self, RGBA=[None, None, None, None], isTarget=0.0, isMeasured=1.0, isFixed=0.0, isSticky=0.0, hasCilia=0.0, 
                     isPaceMaker=0.0, paceMakerPeriod=0.0, signalValueDecay=0.0, signalTimeDelay=0.0, inactivePeriod=0.0, 
                     matModel=0.0, elasticMod=1.0, failStress=0.0, density=1.0, poissonsRatio=0.35, CTE=0.0, 
                     uStatic=1.0, uDynamic=0.8, diff_thresh=0.0): 
        """Adds a new material to the .vxa palette.

        Args:
            RGBA (list, optional): List of 0.0-0.1 RGBA ranges, randomised if none given. Defaults to [None, None, None, None].
            isTarget (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            isMeasured (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 1.0.
            isFixed (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            isSticky (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            hasCilia (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            isPaceMaker (float, optional): 0 for disabled and 1 for enabled, rounds to nearest if neither. Defaults to 0.0.
            paceMakerPeriod (float, optional): Period in seconds between pacemaker signals. Defaults to 0.0.
            signalValueDecay (float, optional): Decay ratio of signal propogation, 0.0 is no propogation and 1.0 is infinite propogation. Defaults to 0.0.
            signalTimeDelay (float, optional): Time delay in seconds for signal propogation. Defaults to 0.0.
            inactivePeriod (float, optional): Time delay in seconds for voxel inactivity after sending a signal. Defaults to 0.0.
            matModel (float, optional): 0 for non-failing model and 1 for failing capable model, rounds to nearest if neither. Defaults to 0.0.
            elasticMod (float, optional): Elastic modulus for the material. Defaults to 1.0.
            failStress (float, optional): Pressure threshold for material failure. Defaults to 0.0.
            density (float, optional): Density of material. Defaults to 1.0.
            poissonsRatio (float, optional): Ratio of stretch. Defaults to 0.35.
            CTE (float, optional): Ration of thermal expansion. Defaults to 0.0.
            uStatic (float, optional): Static friction coefficient. Defaults to 1.0.
            uDynamic (float, optional): Kinetic friction coefficient. Defaults to 0.8.
            diff_thresh (float, optional): Threshold for material similarity, 0 allows identical materials and 100 requires maximal difference. Defaults to 0.0.

        Returns:
            int: The numeric ID of the material.
        """

        properties = {
            "isTarget": 1,
            "isMeasured": 1,
            "Fixed": 1,
            "sticky": 1,
            "Cilia": 1.0,
            "isPaceMaker": 1,
            "PaceMakerPeriod": 1.0,
            "signalValueDecay": 1.0,
            "signalTimeDecay": 1.0,
            "inactivePeriod": 1.0,
            "MatModel": 1,
            "Fail_Stress": 1.0,
            "Elastic_Mod": 10 ** 7,
            "Density": 10 ** 7,
            "Poissons_Ratio": 0.5,
            "CTE": 10 ** -2,
            "uStatic": 5.0,
            "uDynamic": 1.0,
        }

        # === Palette ===
        palette = self.root.find("*/Palette")
        # ==== Material ====
        mat_ID = len(palette.findall("Material")) + 1
        new_mat = etree.Element("Material")
        new_mat.set("ID", str(mat_ID))
        etree.SubElement(new_mat, "Name").text = str("Generated")

        # ===== Display =====
        display = etree.SubElement(new_mat, "Display")
        RGBA = [np.around(np.random.random(), 2) if v==None else v/255 for v in RGBA]
        etree.SubElement(display, "Red").text = str(RGBA[0])
        etree.SubElement(display, "Green").text = str(RGBA[1])
        etree.SubElement(display, "Blue").text = str(RGBA[2])
        etree.SubElement(display, "Alpha").text = str(1)

        # ===== Mechanical =====
        new_mech = etree.SubElement(new_mat, "Mechanical")
        etree.SubElement(new_mech, "isTarget").text = str(round(isTarget))                          # 0 OR 1
        etree.SubElement(new_mech, "isMeasured").text = str(round(isMeasured))                      # 0 OR 1
        etree.SubElement(new_mech, "Fixed").text = str(round(isFixed))                              # 0 OR 1
        etree.SubElement(new_mech, "sticky").text = str(round(isSticky))                            # 0 OR 1
        etree.SubElement(new_mech, "Cilia").text = str(round(hasCilia))                             # 0 OR 1
        etree.SubElement(new_mech, "MatModel").text = str(round(matModel))                          # 0 OR 1
        etree.SubElement(new_mech, "Fail_Stress").text = str(failStress)                            # 0 TO 1

        etree.SubElement(new_mech, "isPaceMaker").text = str(round(isPaceMaker))                    # 0 OR 1
        etree.SubElement(new_mech, "PaceMakerPeriod").text = str((paceMakerPeriod * 0.4) + 0.2)     # 0.2 TO 0.6
        etree.SubElement(new_mech, "signalValueDecay").text = str(signalValueDecay * 0.5)           # 0.0 TO 0.5
        etree.SubElement(new_mech, "signalTimeDecay").text = str((signalTimeDelay * 0.4) + 0.2)     # 0.2 TO 0.6
        etree.SubElement(new_mech, "inactivePeriod").text = str((inactivePeriod * 0.4) + 0.2)       # 0.2 TO 0.6

        etree.SubElement(new_mech, "Elastic_Mod").text = str(10 ** int(4 + (elasticMod * 4)))       # 1e+4 TO 1e+8
        etree.SubElement(new_mech, "Density").text = str(10 ** int(4 + (density * 4)))              # 1e+4 TO 1e+8
        etree.SubElement(new_mech, "Poissons_Ratio").text = str(poissonsRatio * 0.5)                # 0 TO 0.5
        etree.SubElement(new_mech, "CTE").text = str(10 ** -int(CTE + 2))                           # 0 TO 1e-1
        etree.SubElement(new_mech, "uStatic").text = str(uStatic * 5.0)                             # 0 TO 5.0
        etree.SubElement(new_mech, "uDynamic").text = str(uDynamic)                                 # 0 TO 1

        # Check that new_mat is distinct enough from others
        for m, pre_mat in enumerate(palette.findall("Material")):
            pre_mech = pre_mat.find("Mechanical")
            all_diff = 0
            # Skip environment materials
            if int(float(pre_mech.find("Fixed").text)) == 0:
                # Calculate per-property similarity
                for p, prop in enumerate(pre_mech):
                    abs_diff = abs(float(pre_mech.find(prop.tag).text) - float(new_mech.find(prop.tag).text))
                    if (abs_diff == 0): all_diff += 0
                    else:               all_diff += (abs_diff / properties[prop.tag])
                # Return pre-existing similar material
                #per_diff = (all_diff / sum(properties.values())) * 100
                if (all_diff == 0): per_diff = 0
                else:               per_diff = (all_diff / len(properties.values())) * 100
                
                if per_diff <= diff_thresh:
                    return pre_mat.attrib["ID"]

        # New mat is distinct enough, so append to palette
        palette.append(new_mat)
        return mat_ID

    def write(self, filename='base.vxa'):
        """Writes the VXA tree to a file, with proper indenting.

        Args:
            filename (str, optional): Filename for the .vxa file. Defaults to 'base.vxa'.
        """

        # If no material has been added, add default material
        if len(self.root.find("*/Palette").findall("Material")) == 0:
            self.add_material()
        
        with open(filename, 'w+') as f:
            f.write(etree.tostring(self.root, encoding="unicode", pretty_print=True))
