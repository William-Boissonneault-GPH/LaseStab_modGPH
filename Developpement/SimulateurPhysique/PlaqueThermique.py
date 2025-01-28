import numpy as np

class PlaqueThermique():
    def __init__(self, dimensions, matériaux, coefConv, grosseurElementFinie, T_init):

        ###Indication de l'objet est rendu à quelle temps de simulation
        self.time = 0

        ###(largeur, longeur, epaisseur) en [m] 
        self.dimensions = dimensions

        #self.k = Conductivité Thermique [W/m·K]
        #self.rho = Densité [kg/m^3]
        #self.cp = Chaleur spécifique  [J/kg·K]
        #self.alpha = Diffusivité Thermique [m^2/s]
        #self.coefConv = Coeff. de convection[W/m^2·K]
        if type(matériaux) == tuple:
            self.k, self.rho, self.cp = matériaux
        else:
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

        #Grosseur element : largeur de chaque petit cube en (dx, dy)
        ### ! L'utilisateur / code pourrait rentrer des chiffres bizzares (100 / 13)
        ### Nous modifions donc le paramètre pour avoir une division exact
        self.grosseurElement = grosseurElementFinie
        y_amount = int(round(self.dimensions[1]/self.grosseurElement[1]))
        x_amount = int(round(self.dimensions[0]/self.grosseurElement[0]))
        self.grosseurElement = (self.dimensions[0]/x_amount, self.dimensions[1]/y_amount, self.dimensions[2])

        ###TODO: PERMETTRE L'INITIALISATION AVEC UNE FONCTION DE TEMPÉRATURE (PAS QUE UNE TEMPÉRATURE FIXE)
        self.matTemperatureInitiale = np.full((y_amount, x_amount), T_init + 273.15)
        ###CAUTION: Approximation cp constant depuis 0 absolu, ne devrait pas affecter le code (nous jouons avec variations)
        self.matEnergie = self.matTemperatureInitiale * self.rho * self.cp

        ###DICTIONNAIRE DE VALEUR UTILE
        self.dimensionsElementFinie = {
            "dX" : self.grosseurElement[0],
            "dY" :  self.grosseurElement[1],
            "dZ" :  self.grosseurElement[2],
            "Vol" :  self.grosseurElement[0]*self.grosseurElement[1]*self.grosseurElement[2],
            "AireDessu" : self.grosseurElement[0]*self.grosseurElement[1],
            "AireCLong" : self.grosseurElement[0]*self.grosseurElement[2],
            "AireCCourt" : self.grosseurElement[1]*self.grosseurElement[2]
        }
        

        ###OPTIMIZATION: utilise beaucoup de mémoire
        ###                 pas nécessairement nécessaire si nous avons directement les points que nous voulons les échelons
        ###               -> Prendre l'historique des températures aux points désiré et render l'animation sans conserver l'historique
        self.historiqueEnergie = [self.matEnergie]
        pass


    def propagationDunPasDeTemps(self, dTime, *matsEnergiePerturbation):
        #Fonction qui permet d'avancer dans le temps
        #Matrice d'energie de perturbation en [W/m^3 s]

        #TODO: matConduction
        #matConduction = np.array [2d]  ---> Matrice d'énergie reçu ou perdu dans chaque petit élement de volume par conduction uniquement
        matConduction = np.zeros_like(self.matEnergie)
            #TODO: Gerer les edge case, pour l'instant que la partie centrale conduit
        matConduction[1:-1,1:-1] =((self.k * dTime) / (self.dimensionsElementFinie["dX"]**2)) * ( 
            self.matEnergie[1:-1,0:-2] +
            self.matEnergie[1:-1,2:] -
            2*self.matEnergie[1:-1,1:-1]) +((self.k * dTime) / (self.dimensionsElementFinie["dY"]**2)) * (
            self.matEnergie[0:-2,1:-1] +
            self.matEnergie[2:,1:-1] -
            2*self.matEnergie[1:-1,1:-1])



        #TODO: matConduction
        #matConvection = np.array [2d]  ---> Matrice d'énergie perdu dans chaque petit élement de volume par convection uniquement
        matConvection = np.zeros_like(self.matEnergie)







        self.matEnergie = self.matEnergie + matConduction + matConvection
        
        for matEnergiePertubation in matsEnergiePerturbation[0]:
            self.matEnergie += (matEnergiePertubation / self.dimensionsElementFinie["Vol"]) * dTime


        ###OPTIMIZATION: utilise beaucoup de mémoire
        ###                 pas nécessairement nécessaire si nous avons directement les points que nous voulons les échelons
        ###               -> Prendre l'historique des températures aux points désiré et render l'animation sans conserver l'historique
        self.historiqueEnergie.append(self.matEnergie)
        self.time += dTime

        return self.matEnergie
    
    def recolterMatTemperature(self):
        self.matTemperature = (self.matEnergie / (self.rho * self.cp) ) - 273.15
        return self.matTemperature