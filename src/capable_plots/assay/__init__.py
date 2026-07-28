"""Assay domain pack — generic dose-response math and the recurring assay figures.

Leak-safe: contains only generic science (textbook 4PL, standard figure grammar).
Capable-internal specifics — targets, control handling, the results tracker — stay
in the calling workspace.
"""
from __future__ import annotations

from . import curves, plots
from .curves import FitResult, fit_4pl, four_pl
from .plots import dose_response, group_box

__all__ = [
    "FitResult",
    "curves",
    "dose_response",
    "fit_4pl",
    "four_pl",
    "group_box",
    "plots",
]
