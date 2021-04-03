from fastargs import Section, Param

Section('imported_section.blah').params(
    p1=Param(float, required=True)
)
