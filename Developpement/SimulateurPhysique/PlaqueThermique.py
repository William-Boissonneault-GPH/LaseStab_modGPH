class PlaqueThermique():
    def __init__(self, dimensions, matériaux, coefConv):
        ###(largeur, longeur, epaisseur) en [m] 
        self.dimensions = dimensions   

        #self.k = Conductivité Thermique [W/m·K]
        #self.rho = Densité [kg/m^3]
        #self.cp = Chaleur spécifique  [J/kg·K]
        #self.alpha = Diffusivité Thermique [m^2/s]
        #self.coefConv = Coeff. de convection[W/m^2·K]

        match matériaux:
            case "Aluminium":
                self.k = 205
                self.rho = 2700
                self.cp = 900
            case "Cuivre":
                self.k = 1
                self.rho = 2
                self.cp = 3

        self.alpha = self.k / (self.rho * self.cp)

        self.coefConv = coefConv
        pass

    def propagate(self, dTime):
        pass