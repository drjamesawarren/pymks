import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import metrics
mse = metrics.mean_squared_error

class MKSRegressionModel(LinearRegression):
    r"""
    The `MKSRegressionModel` fits data using the Materials Knowledge
    System in Fourier Space. Currently, the model assumes that the
    microstructure (`X`) must varies only between 0 and 1.

    The following demonstrates how to the viability of the
    `MKSRegressionModel` with a simple 1D filter.

    >>> Nbin = 101
    >>> Nspace = 81
    >>> Nsample = 400

    Define a filter function.

    >>> def filter(x):
    ...     return np.where(x < 10,
    ...                     np.exp(-abs(x)) * np.cos(x * np.pi),
    ...                     np.exp(-abs(x - 20)) * np.cos((x - 20) * np.pi))

    Use the filter function to construct some coefficients.

    >>> coeff = np.linspace(1, 0, Nbin)[None,:] * filter(np.linspace(0, 20, Nspace))[:,None]
    >>> Fcoeff = np.fft.fft(coeff, axis=0)

    Make some test samples.

    >>> np.random.seed(2)
    >>> X = np.random.random((Nsample, Nspace))

    Construct a response with the `Fcoeff`.

    >>> H = np.linspace(0, 1, Nbin)
    >>> X_ = np.maximum(1 - abs(X[:,:,None] - H) / (H[1] - H[0]), 0)
    >>> FX = np.fft.fft(X_, axis=1)
    >>> Fy = np.sum(Fcoeff[None] * FX, axis=-1)
    >>> y = np.fft.ifft(Fy, axis=1).real

    Use the `MKSRegressionModel` to reconstruct the coefficients

    >>> model = MKSRegressionModel(Nbin=Nbin)
    >>> model.fit(X, y)
    >>> model.coeff = np.fft.ifft(model.Fcoeff, axis=0)

    Check the result
    
    >>> assert mse(coeff, model.coeff) < 1e-3

    """
    
    def __init__(self, Nbin=10):
        r"""
        Create an `MKSRegressionModel`.

        :Parameters:
         - `Nbin`: is the number of discretization bins for the
           "microstructure".
        """
        
        self.Nbin = Nbin

    def _axes(self, X):
        r"""
        Return the axes argument for `fftn`.

        >>> X = np.zeros((5, 2, 2, 2))
        >>> print MKSRegressionModel()._axes(X)
        [1 2 3]
        """
        
        return np.arange(len(X.shape) - 1) + 1
        
    def _bin(self, X):
        """
        Bin the microstructure.

        >>> Nbin = 10
        >>> np.random.seed(4)
        >>> X = np.random.random((2, 5, 3, 2))
        >>> X_ = MKSRegressionModel(Nbin)._bin(X)
        >>> H = np.linspace(0, 1, Nbin)
        >>> Xtest = np.sum(X_ * H[None,None,None,:], axis=-1)
        >>> assert np.allclose(X, Xtest)

        """
        
        H = np.linspace(0, 1, self.Nbin)
        dh = H[1] - H[0]
        return np.maximum(1 - abs(X[..., None] - H) / dh, 0)

    def _binfft(self, X):
        r"""
        Bin the microstructure and take the Fourier transform.

        >>> Nbin = 10
        >>> np.random.seed(3)
        >>> X = np.random.random((2, 5, 3))
        >>> FX_ = MKSRegressionModel(Nbin)._binfft(X)
        >>> X_ = np.fft.ifftn(FX_, axes=(1, 2))
        >>> H = np.linspace(0, 1, Nbin)
        >>> Xtest = np.sum(X_ * H[None,None,None,:], axis=-1)
        >>> assert np.allclose(X, Xtest)

        """
        Xbin = np.array([self._bin(Xi) for Xi in X])
        return np.fft.fftn(Xbin, axes=self._axes(X))
        
    def fit(self, X, y):
        r"""
        Fits the data by calculating a set of influence coefficients,
        `Fcoeff`.

        >>> X = np.linspace(0, 1, 4).reshape((1, 2, 2))
        >>> y = X.swapaxes(1, 2)
        >>> model = MKSRegressionModel(Nbin=2)
        >>> model.fit(X, y)
        >>> assert np.allclose(model.Fcoeff, [[[ 0.5,  0.5 ],  [-1,  1  ]],
        ...                                   [[-0.25, 0.25], [-0.5, 0.5]]])


        :Parameters:
         - `X`: the microstructre, an `(S, N, ...)` shaped array where
           `S` is the number of samples and `N` is the spatial
           discretization.
         - `y`: the response, same shape as 
        """
        
        assert len(y.shape) > 1
        assert y.shape == X.shape
        FX = self._binfft(X)
        Fy = np.fft.fftn(y, axes=self._axes(X))
        s = X.shape[1:]
        self.Fcoeff = np.zeros(s + (self.Nbin,), dtype=np.complex)
        sl = (slice(None),)
        for ijk in np.ndindex(s):
            self.Fcoeff[ijk + sl] = np.linalg.lstsq(FX[sl + ijk + sl], Fy[sl + ijk])[0]
                
    def predict(self, X):
        r"""
        Calculates a response from the microstructure `X`.

        >>> X = np.linspace(0, 1, 4).reshape((1, 2, 2))
        >>> y = X.swapaxes(1, 2)
        >>> model = MKSRegressionModel(Nbin=2)
        >>> model.fit(X, y)
        >>> assert np.allclose(y, model.predict(X))

        :Parameters:
         - `X`: the microstructre, an `(S, N, ...)` shaped array where
           `S` is the number of samples and `N` is the spatial
           discretization.

        :Return:
         - the response, same shape as `X`
           
        """
        assert X.shape[1:] == self.Fcoeff.shape[:-1]
        FX = self._binfft(X)
        Fy = np.sum(FX * self.Fcoeff[None,...], axis=-1)
        return np.fft.ifftn(Fy, axes=self._axes(X)).real

if __name__ == '__main__':
    import fipy.tests.doctestPlus
    exec(fipy.tests.doctestPlus._getScript())