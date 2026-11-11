"""Rerun the established raw-score/memory audits into the separate revision only."""
from pathlib import Path
import shutil,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'paper/revised_aaai'
if not (OUT/'vendor').exists():shutil.copytree(ROOT/'output/final_aaai/vendor',OUT/'vendor')
import build_final_paper
build_final_paper.OUT=OUT
build_final_paper.main()
import verify_final_scores
verify_final_scores.OUT=OUT
verify_final_scores.main()
