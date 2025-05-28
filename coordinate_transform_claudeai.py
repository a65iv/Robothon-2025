import numpy as np
from scipy.optimize import least_squares
from scipy.interpolate import griddata

# Extracted data points from the image grid (world_x, world_y, pixel_x, pixel_y)
sample_points = [
    # Row 1 (world_y = 750)
    (-150, 750, 2.8, 101.8),
    (-100, 750, 101.8, 101.8), 
    (-50, 750, 186.6, 186.6),
    (0, 750, 319.7, 319.7),
    (50, 750, 395.8, 395.8),
    (100, 750, 495.8, 495.8),
    (150, 750, 591.7, 591.7),
    
    # Row 2 (world_y = 700) 
    (-150, 700, 2.8, 264.2),
    (-100, 700, 101.8, 264.2),
    (-50, 700, 186.6, 320.2),
    (0, 700, 319.7, 399.5),
    (50, 700, 395.8, 496.1),
    (100, 700, 495.8, 562.2),
    (150, 700, 591.7, 632.2),
    
    # Row 3 (world_y = 650)
    (-150, 650, 2.8, 345.2),
    (-100, 650, 101.8, 345.2),
    (-50, 650, 186.6, 399.5),
    (0, 650, 319.7, 482.2),
    (50, 650, 395.8, 517.5),
    (100, 650, 495.8, 667.5),
    (150, 650, 591.7, 584.3),
    
    # Row 4 (world_y = 600)
    (-150, 600, 2.8, 417.2),
    (-100, 600, 101.8, 506.2),
    (-50, 600, 186.6, 506.2),
    (0, 600, 319.7, 526.3),
    (50, 600, 395.8, 598.6),
    (100, 600, 495.8, 649.4),
    (150, 600, 591.7, 587.4),
    
    # Row 5 (world_y = 550)
    (-150, 550, 2.8, 498.1),
    (-100, 550, 101.8, 598.1),
    (-50, 550, 186.6, 506.6),
    (0, 550, 319.7, 619.6),
    (50, 550, 395.8, 598.6),
    (100, 550, 495.8, 492.7),
    (150, 550, 591.7, 659.5),
]

class PixelWorldTransformer:
    def __init__(self):
        self.sample_points = np.array(sample_points)
        self.world_coords = self.sample_points[:, :2]  # world_x, world_y
        self.pixel_coords = self.sample_points[:, 2:]  # pixel_x, pixel_y
        
        # Fit multiple models and choose the best one
        self.models = self._fit_all_models()
        self.best_model_name = self._select_best_model()
        
        print(f"Selected model: {self.best_model_name}")
        print(f"Model RMSE: {self.models[self.best_model_name]['rmse']:.2f} pixels")
    
    def _fit_all_models(self):
        """Fit different transformation models and return their parameters"""
        models = {}
        
        # 1. Linear model
        models['linear'] = self._fit_linear_model()
        
        # 2. Polynomial model (2nd order)
        models['polynomial'] = self._fit_polynomial_model()
        
        # 3. Perspective transformation
        models['perspective'] = self._fit_perspective_model()
        
        return models
    
    def _fit_linear_model(self):
        """Fit a simple linear transformation: pixel = A * world + B"""
        def residuals(params):
            a, b, c, d = params
            predicted_x = a * self.world_coords[:, 0] + b
            predicted_y = c * self.world_coords[:, 1] + d
            
            error_x = predicted_x - self.pixel_coords[:, 0]
            error_y = predicted_y - self.pixel_coords[:, 1]
            return np.concatenate([error_x, error_y])
        
        # Initial guess based on rough analysis
        initial_params = [2.0, 320, -2.0, 850]
        result = least_squares(residuals, initial_params)
        rmse = np.sqrt(np.mean(residuals(result.x)**2))
        
        return {'params': result.x, 'rmse': rmse, 'type': 'linear'}
    
    def _fit_polynomial_model(self):
        """Fit a 2nd order polynomial transformation"""
        def residuals(params):
            # Unpack parameters
            a1, a2, a3, b1, c1, c2, c3, d1 = params
            
            wx, wy = self.world_coords[:, 0], self.world_coords[:, 1]
            
            # 2nd order polynomial
            predicted_x = a1 * wx + a2 * wx**2 + a3 * wx * wy + b1
            predicted_y = c1 * wy + c2 * wy**2 + c3 * wx * wy + d1
            
            error_x = predicted_x - self.pixel_coords[:, 0]
            error_y = predicted_y - self.pixel_coords[:, 1]
            return np.concatenate([error_x, error_y])
        
        # Initial guess
        initial_params = [2.0, 0.001, 0.001, 320, -2.0, 0.001, 0.001, 850]
        result = least_squares(residuals, initial_params)
        rmse = np.sqrt(np.mean(residuals(result.x)**2))
        
        return {'params': result.x, 'rmse': rmse, 'type': 'polynomial'}
    
    def _fit_perspective_model(self):
        """Fit a perspective transformation (homography)"""
        def residuals(params):
            h11, h12, h13, h21, h22, h23, h31, h32 = params
            # h33 = 1 (normalization)
            
            wx, wy = self.world_coords[:, 0], self.world_coords[:, 1]
            
            # Homogeneous coordinates
            denominator = h31 * wx + h32 * wy + 1
            predicted_x = (h11 * wx + h12 * wy + h13) / denominator
            predicted_y = (h21 * wx + h22 * wy + h23) / denominator
            
            error_x = predicted_x - self.pixel_coords[:, 0]
            error_y = predicted_y - self.pixel_coords[:, 1]
            return np.concatenate([error_x, error_y])
        
        # Initial guess for perspective transformation
        initial_params = [2.0, 0.0, 320, 0.0, -2.0, 850, 0.0001, 0.0001]
        result = least_squares(residuals, initial_params)
        rmse = np.sqrt(np.mean(residuals(result.x)**2))
        
        return {'params': result.x, 'rmse': rmse, 'type': 'perspective'}
    
    def _select_best_model(self):
        """Select the model with the lowest RMSE"""
        best_model = min(self.models.keys(), key=lambda k: self.models[k]['rmse'])
        return best_model
    
    def pixel_to_world(self, pixel_x, pixel_y):
        """Convert pixel coordinates to world coordinates using the best model"""
        if self.best_model_name == 'linear':
            return self._linear_pixel_to_world(pixel_x, pixel_y)
        elif self.best_model_name == 'polynomial':
            return self._polynomial_pixel_to_world(pixel_x, pixel_y)
        elif self.best_model_name == 'perspective':
            return self._perspective_pixel_to_world(pixel_x, pixel_y)
        else:
            # Fallback to interpolation
            return self._interpolation_pixel_to_world(pixel_x, pixel_y)
    
    def _linear_pixel_to_world(self, px, py):
        """Inverse linear transformation"""
        a, b, c, d = self.models['linear']['params']
        world_x = (px - b) / a
        world_y = (py - d) / c
        return float(world_x), float(world_y)
    
    def _polynomial_pixel_to_world(self, px, py):
        """Inverse polynomial transformation (using numerical approximation)"""
        # For polynomial inverse, we use optimization to find world coords
        def error_func(world_coords):
            wx, wy = world_coords
            a1, a2, a3, b1, c1, c2, c3, d1 = self.models['polynomial']['params']
            
            pred_px = a1 * wx + a2 * wx**2 + a3 * wx * wy + b1
            pred_py = c1 * wy + c2 * wy**2 + c3 * wx * wy + d1
            
            return [(pred_px - px)**2 + (pred_py - py)**2]
        
        # Initial guess using linear approximation
        wx_init, wy_init = self._linear_pixel_to_world(px, py)
        result = least_squares(error_func, [wx_init, wy_init])
        return float(result.x[0]), float(result.x[1])
    
    def _perspective_pixel_to_world(self, px, py):
        """Inverse perspective transformation"""
        h11, h12, h13, h21, h22, h23, h31, h32 = self.models['perspective']['params']
        
        # Solve the perspective transformation inverse
        # This requires solving a system of equations
        def error_func(world_coords):
            wx, wy = world_coords
            denominator = h31 * wx + h32 * wy + 1
            pred_px = (h11 * wx + h12 * wy + h13) / denominator
            pred_py = (h21 * wx + h22 * wy + h23) / denominator
            return [(pred_px - px)**2 + (pred_py - py)**2]
        
        # Initial guess
        wx_init, wy_init = self._linear_pixel_to_world(px, py)
        result = least_squares(error_func, [wx_init, wy_init])
        return float(result.x[0]), float(result.x[1])
    
    def _interpolation_pixel_to_world(self, px, py):
        """Fallback method using interpolation"""
        # Use griddata for interpolation
        world_x = griddata(self.pixel_coords, self.world_coords[:, 0], 
                          (px, py), method='cubic', fill_value=np.nan)
        world_y = griddata(self.pixel_coords, self.world_coords[:, 1], 
                          (px, py), method='cubic', fill_value=np.nan)
        
        if np.isnan(world_x) or np.isnan(world_y):
            # Fall back to linear if cubic fails
            world_x = griddata(self.pixel_coords, self.world_coords[:, 0], 
                              (px, py), method='linear')
            world_y = griddata(self.pixel_coords, self.world_coords[:, 1], 
                              (px, py), method='linear')
        
        return float(world_x), float(world_y)
    
    def world_to_pixel(self, world_x, world_y):
        """Convert world coordinates to pixel coordinates"""
        if self.best_model_name == 'linear':
            a, b, c, d = self.models['linear']['params']
            pixel_x = a * world_x + b
            pixel_y = c * world_y + d
            return float(pixel_x), float(pixel_y)
        
        elif self.best_model_name == 'polynomial':
            a1, a2, a3, b1, c1, c2, c3, d1 = self.models['polynomial']['params']
            pixel_x = a1 * world_x + a2 * world_x**2 + a3 * world_x * world_y + b1
            pixel_y = c1 * world_y + c2 * world_y**2 + c3 * world_x * world_y + d1
            return float(pixel_x), float(pixel_y)
        
        elif self.best_model_name == 'perspective':
            h11, h12, h13, h21, h22, h23, h31, h32 = self.models['perspective']['params']
            denominator = h31 * world_x + h32 * world_y + 1
            pixel_x = (h11 * world_x + h12 * world_y + h13) / denominator
            pixel_y = (h21 * world_x + h22 * world_y + h23) / denominator
            return float(pixel_x), float(pixel_y)
    
    def test_accuracy(self):
        """Test the transformation accuracy on sample points"""
        print("\nAccuracy Test:")
        print("=" * 60)
        print(f"{'World Coords':<15} {'Pixel Coords':<15} {'Predicted':<15} {'Error':<10}")
        print("-" * 60)
        
        total_error = 0
        for point in self.sample_points:
            world_x, world_y, true_px, true_py = point
            pred_wx, pred_wy = self.pixel_to_world(true_px, true_py)
            
            error_x = abs(pred_wx - world_x)
            error_y = abs(pred_wy - world_y)
            total_error += np.sqrt(error_x**2 + error_y**2)
            
            print(f"({world_x:4.0f},{world_y:4.0f})     ({true_px:5.1f},{true_py:5.1f})     ({pred_wx:5.1f},{pred_wy:5.1f})     {np.sqrt(error_x**2 + error_y**2):5.1f}")
        
        avg_error = total_error / len(self.sample_points)
        print(f"\nAverage World Coordinate Error: {avg_error:.2f} units")

# Create the transformer and test it
def create_transformer():
    """Create and return the coordinate transformer"""
    transformer = PixelWorldTransformer()
    transformer.test_accuracy()
    return transformer

# Example usage
if __name__ == "__main__":
    # Create the transformer
    transformer = create_transformer()
    
    # Example conversions
    print("\n" + "="*50)
    print("Example Conversions:")
    print("="*50)
    
    # Test some conversions
    test_pixels = [(300, 400), (100, 200), (500, 600), (400, 300)]
    
    for px, py in test_pixels:
        wx, wy = transformer.pixel_to_world(px, py)
        # Verify by converting back
        px_back, py_back = transformer.world_to_pixel(wx, wy)
        
        print(f"Pixel ({px}, {py}) → World ({wx:.1f}, {wy:.1f}) → Pixel ({px_back:.1f}, {py_back:.1f})")
    
    print(f"\nUse transformer.pixel_to_world(px, py) for your conversions!")
