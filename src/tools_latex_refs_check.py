#!/usr/bin/env python3
"""
tools_latex_refs_check.py - Enhanced LaTeX/Markdown reference checker for RH paper

Validates citations, labels, cross-references, and document structure.

Usage:
    python tools_latex_refs_check.py <file.tex|file.md> [options]
    
Options:
    --verbose    Show detailed analysis
    --strict     Check for additional style issues
    --output     Save report to file
"""

import sys
import re
import pathlib
import argparse
import json
from collections import defaultdict
from datetime import datetime

# Required citations for the RH paper
REQUIRED_CITATIONS = {
    "tao_suppl2": "Tao's supplement on truncated log-derivative framework",
    "patel_yang_subweyl": "Explicit sub-Weyl bound |ζ(1/2+it)| ≤ 66.7t^(27/164)",
    "dlmf_ch5": "NIST DLMF Chapter 5 (Gamma function, Stirling)",
    "proofwiki_modsin": "Modulus identity: |sin(x+iy)| = sqrt(sin²x + sinh²y)"
}

# Expected equation labels
EXPECTED_EQUATIONS = [
    "phase-identity",     # (2.1) Phase identity from argument principle
    "bridge-L-D",        # (2.2) Bridge from L to D
    "strip-bound",       # (2.3) Thin strip bound
    "right-edge",        # (2.4) Right edge bound
    "horizontals",       # (2.5) Horizontal bound
    "master-reduction",  # (2.6) Master inequality
    "boundary-growth",   # (3.1) B(s;R0) bound
    "disc-control",      # (4.1) and (4.2) g_R0 bounds
    "thin-strip-final",  # (5.1) to (5.3) C_thin* bounds
    "right-constant",    # (6.1) C_right bound
    "horiz-diff",        # (6.2) Horizontal difference
    "master-final",      # (7.1) Final form
    "log-T0"            # (7.2) Threshold definition
]

# Expected sections
EXPECTED_SECTIONS = {
    "1": "Introduction and main theorem",
    "2": "Setup and phase identity", 
    "3": "Boundary growth on discs",
    "4": "Disc control for the truncated log-derivative",
    "5": "Thin-strip estimate",
    "6": "Right edge and horizontals",
    "7": "Master inequality and proof of Theorem 1",
    "8": "Notes on Sources & Attribution",
    "9": "Constants and parameters",
    "10": "Glossary",
    "11": "Related work"
}

class ReferenceChecker:
    """Comprehensive reference checker for academic documents."""
    
    def __init__(self, filepath, verbose=False, strict=False):
        self.filepath = pathlib.Path(filepath)
        self.verbose = verbose
        self.strict = strict
        self.content = self._load_file()
        self.is_latex = filepath.endswith('.tex')
        self.is_markdown = filepath.endswith('.md')
        
        # Results storage
        self.citations_found = set()
        self.labels_defined = set()
        self.labels_referenced = set()
        self.sections_found = []
        self.equations_found = set()
        self.issues = []
        self.warnings = []
        
    def _load_file(self):
        """Load file content."""
        try:
            return self.filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    
    def extract_citations(self):
        """Extract all citations."""
        # LaTeX: \cite{key}, \Cite{key}, \citep{key}, etc.
        patterns = [
            r'\\cite[pt]?\{([^}]+)\}',
            r'\\Cite\{([^}]+)\}',
            r'\\bibitem\{([^}]+)\}'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.content)
            for match in matches:
                # Handle multiple citations like \cite{key1,key2}
                for cite in match.split(','):
                    self.citations_found.add(cite.strip())
        
        # Markdown style: [CITE: key] or similar
        md_patterns = [
            r'\[CITE:\s*([^\]]+)\]',
            r'\[@([^\]]+)\]',  # Pandoc style
            r'\^\[([^\]]+)\]'  # Footnote style
        ]
        
        for pattern in md_patterns:
            matches = re.findall(pattern, self.content)
            for match in matches:
                self.citations_found.add(match.strip())
        
        if self.verbose:
            print(f"\nFound {len(self.citations_found)} unique citations:")
            for cite in sorted(self.citations_found):
                print(f"  - {cite}")
    
    def extract_labels_and_refs(self):
        """Extract labels and references."""
        # Labels
        label_patterns = [
            r'\\label\{([^}]+)\}',
            r'\\tag\{([^}]+)\}',  # Sometimes used for equations
        ]
        
        for pattern in label_patterns:
            matches = re.findall(pattern, self.content)
            self.labels_defined.update(matches)
        
        # References
        ref_patterns = [
            r'\\ref\{([^}]+)\}',
            r'\\eqref\{([^}]+)\}',
            r'\\pageref\{([^}]+)\}',
            r'\\autoref\{([^}]+)\}',
            r'\\cref\{([^}]+)\}',
            r'\\Cref\{([^}]+)\}'
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, self.content)
            self.labels_referenced.update(matches)
        
        # Extract equations specifically
        self.equations_found = {
            label for label in self.labels_defined 
            if any(kw in label.lower() for kw in ['eq', 'equation', 'formula'])
        }
    
    def extract_sections(self):
        """Extract document structure."""
        if self.is_latex:
            # LaTeX sections
            patterns = [
                (r'\\section\*?\{([^}]+)\}', 'section'),
                (r'\\subsection\*?\{([^}]+)\}', 'subsection'),
                (r'\\subsubsection\*?\{([^}]+)\}', 'subsubsection'),
                (r'\\chapter\*?\{([^}]+)\}', 'chapter')
            ]
            
            for pattern, level in patterns:
                matches = re.findall(pattern, self.content)
                for match in matches:
                    self.sections_found.append((level, match))
        
        elif self.is_markdown:
            # Markdown headers
            lines = self.content.split('\n')
            for line in lines:
                if line.startswith('#'):
                    level = len(re.match(r'^#+', line).group())
                    title = line.strip('#').strip()
                    if title:
                        self.sections_found.append((f'h{level}', title))
    
    def check_missing_required(self):
        """Check for missing required citations."""
        missing_citations = set(REQUIRED_CITATIONS.keys()) - self.citations_found
        
        if missing_citations:
            for cite in missing_citations:
                self.issues.append(f"Missing required citation: {cite} ({REQUIRED_CITATIONS[cite]})")
    
    def check_undefined_references(self):
        """Check for references to undefined labels."""
        undefined = self.labels_referenced - self.labels_defined
        
        if undefined:
            for ref in undefined:
                self.issues.append(f"Reference to undefined label: {ref}")
    
    def check_unused_labels(self):
        """Check for defined but unused labels."""
        unused = self.labels_defined - self.labels_referenced
        
        if unused and self.strict:
            for label in unused:
                self.warnings.append(f"Unused label: {label}")
    
    def check_equation_numbering(self):
        """Check equation numbering consistency."""
        # Look for equation numbers like (2.1), (2.2), etc.
        eq_numbers = re.findall(r'\((\d+\.\d+)\)', self.content)
        
        if eq_numbers:
            # Check for gaps or duplicates
            unique_numbers = set(eq_numbers)
            if len(unique_numbers) < len(eq_numbers):
                self.warnings.append("Duplicate equation numbers found")
            
            # Check sequential ordering
            sorted_numbers = sorted(eq_numbers, key=lambda x: tuple(map(int, x.split('.'))))
            if eq_numbers != sorted_numbers and self.strict:
                self.warnings.append("Equation numbers not in sequential order")
    
    def check_section_structure(self):
        """Verify expected sections are present."""
        section_titles = [title for _, title in self.sections_found]
        
        for num, expected_title in EXPECTED_SECTIONS.items():
            # Check if section number and approximate title match
            found = False
            for title in section_titles:
                if num in title or expected_title.lower() in title.lower():
                    found = True
                    break
            
            if not found and self.strict:
                self.warnings.append(f"Expected section {num} '{expected_title}' not found")
    
    def generate_report(self):
        """Generate comprehensive report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'file': str(self.filepath),
            'summary': {
                'citations_found': len(self.citations_found),
                'labels_defined': len(self.labels_defined),
                'labels_referenced': len(self.labels_referenced),
                'sections_found': len(self.sections_found),
                'issues': len(self.issues),
                'warnings': len(self.warnings)
            },
            'details': {
                'citations': sorted(list(self.citations_found)),
                'missing_required': sorted(list(set(REQUIRED_CITATIONS.keys()) - self.citations_found)),
                'undefined_refs': sorted(list(self.labels_referenced - self.labels_defined)),
                'unused_labels': sorted(list(self.labels_defined - self.labels_referenced)),
                'sections': self.sections_found
            },
            'issues': self.issues,
            'warnings': self.warnings
        }
        
        return report
    
    def run_all_checks(self):
        """Run all validation checks."""
        print(f"\nChecking {self.filepath.name}...")
        print("="*60)
        
        # Extract elements
        self.extract_citations()
        self.extract_labels_and_refs()
        self.extract_sections()
        
        # Run checks
        self.check_missing_required()
        self.check_undefined_references()
        self.check_unused_labels()
        self.check_equation_numbering()
        self.check_section_structure()
        
        # Print results
        print(f"\nFound {len(self.citations_found)} citations")
        print(f"Found {len(self.labels_defined)} labels defined")
        print(f"Found {len(self.labels_referenced)} labels referenced")
        print(f"Found {len(self.sections_found)} sections")
        
        if self.issues:
            print(f"\n❌ ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  - {issue}")
        else:
            print("\n✓ No critical issues found")
        
        if self.warnings and self.verbose:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        return self.generate_report()

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced reference checker for LaTeX/Markdown documents"
    )
    parser.add_argument("file", help="Path to .tex or .md file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed analysis")
    parser.add_argument("--strict", "-s", action="store_true",
                       help="Enable strict checking")
    parser.add_argument("--output", "-o", help="Save report to file")
    
    args = parser.parse_args()
    
    # Create checker
    checker = ReferenceChecker(args.file, verbose=args.verbose, strict=args.strict)
    
    # Run checks
    report = checker.run_all_checks()
    
    # Save report if requested
    if args.output:
        output_path = pathlib.Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {output_path}")
    
    # Exit with error code if issues found
    sys.exit(1 if report['issues'] else 0)

if __name__ == "__main__":
    main()
