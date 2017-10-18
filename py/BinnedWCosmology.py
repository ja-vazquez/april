## This is a CDM cosmology with w

from LCDMCosmology import *
import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import quad

class BinnedWCosmology(LCDMCosmology):
    def __init__(self, dz=0.2, zmax=1.0):
        ## two parameters: Om and h
        self.zbins=np.arange(0,zmax,dz)
        self.Nb=len(self.zbins)
        self.wvals=np.ones(self.Nb)*-1.0
        self.pnames=["w%i"%i for i in range(self.Nb)]
        LCDMCosmology.__init__(self)
        self.integrateOmega()
        
    ## my free parameters. We add Ok on top of LCDM ones (we inherit LCDM)
    def freeParameters(self):
        wpars=[Parameter(name,self.wvals[i]) for i,name in enumerate(self.pnames)]
        return wpars+LCDMCosmology.freeParameters(self)

    def updateParams(self,pars):
        ok=LCDMCosmology.updateParams(self,pars)
        if not ok:
            return False
        gotone=False
        for p in pars:
            if p.name in self.pnames:
                i=self.pnames.index(p.name)
                self.wvals[i]=p.value
                gotone=True
        if gotone:
            self.integrateOmega()
        return True

    def integrateOmega(self):
        abins=np.hstack((1./(1+self.zbins),[1e-4]))
        w=np.hstack((self.wvals,[self.wvals[-1]]))
        itg=interp1d(np.log(abins),3*(1+w))
        oabins=np.hstack((np.logspace(-4,-1,10),np.linspace(0.1,1,100)))
        olnrho=[quad(itg,np.log(a),0)[0] for a in oabins]
        self.DEomega=interp1d(oabins,olnrho)
                        
        
    
    ## this is relative hsquared as a function of a
    ## i.e. H(z)^2/H(z=0)^2
    def RHSquared_a(self,a):
        NuContrib=self.NuDensity.rho(a)/self.h**2
        return (self.Ocb/a**3+self.Omrad/a**4+NuContrib+(1.0-self.Om)*np.exp(self.DEomega(a)))


