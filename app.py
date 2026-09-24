import os
from flask import Flask, render_template
from chambres import bp_chambres
from compte import bp_compte
import bd