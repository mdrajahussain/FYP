"""
Image quality metrics: PSNR, SSIM, MSE, SNR.
"""
import numpy as np


class QualityMetrics:
    """Compute perceptual / statistical quality metrics between two images."""

    @staticmethod
    def psnr(original: np.ndarray, modified: np.ndarray) -> float:
        """Peak Signal-to-Noise Ratio (dB). Higher = better."""
        mse = np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2)
        if mse == 0:
            return float("inf")
        return 20.0 * np.log10(255.0 / np.sqrt(mse))

    @staticmethod
    def ssim(original: np.ndarray, modified: np.ndarray) -> float:
        """
        Structural Similarity Index (Wang et al., 2004).
        Uses scikit-image when available; falls back to a Gaussian-window
        implementation otherwise.
        """
        try:
            from skimage.metrics import structural_similarity
            return float(
                structural_similarity(
                    original.astype(np.float64),
                    modified.astype(np.float64),
                    data_range=255.0,
                    win_size=11,
                    gaussian_weights=True,
                    sigma=1.5,
                    use_sample_covariance=False,
                )
            )
        except ImportError:
            pass

        # ── manual fallback ─────────────────────────────────────────────────
        from scipy.ndimage import gaussian_filter

        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        sigma = 1.5

        a = original.astype(np.float64)
        b = modified.astype(np.float64)

        mu_a  = gaussian_filter(a, sigma)
        mu_b  = gaussian_filter(b, sigma)
        mu_aa = mu_a * mu_a
        mu_bb = mu_b * mu_b
        mu_ab = mu_a * mu_b

        sig_aa = gaussian_filter(a * a, sigma) - mu_aa
        sig_bb = gaussian_filter(b * b, sigma) - mu_bb
        sig_ab = gaussian_filter(a * b, sigma) - mu_ab

        num  = (2 * mu_ab + C1) * (2 * sig_ab + C2)
        den  = (mu_aa + mu_bb + C1) * (sig_aa + sig_bb + C2)
        smap = np.where(den > 0, num / den, 1.0)

        p = 5  # crop border to avoid edge effects
        return float(smap[p:-p, p:-p].mean())

    @staticmethod
    def mse(original: np.ndarray, modified: np.ndarray) -> float:
        """Mean Squared Error. Lower = better."""
        return float(
            np.mean((original.astype(np.float64) - modified.astype(np.float64)) ** 2)
        )

    @staticmethod
    def snr(original: np.ndarray, modified: np.ndarray) -> float:
        """Signal-to-Noise Ratio (dB). Higher = better."""
        sig_power   = np.mean(original.astype(np.float64) ** 2)
        noise_power = np.mean(
            (original.astype(np.float64) - modified.astype(np.float64)) ** 2
        )
        if noise_power == 0:
            return float("inf")
        return 10.0 * np.log10(sig_power / noise_power)

    @staticmethod
    def assess(psnr_val: float) -> str:
        """Human-readable quality assessment based on PSNR."""
        if psnr_val == float("inf"):
            return "Perfect (identical images)"
        if psnr_val > 40:
            return "Excellent (imperceptible changes)"
        if psnr_val > 30:
            return "Good (minor changes)"
        if psnr_val > 20:
            return "Fair (noticeable changes)"
        return "Poor (significant degradation)"