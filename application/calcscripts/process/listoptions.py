from application.calcscripts.process.calcmodels import FaASCE710, AISCSectionsRectangular, AISCSectionsCircular, AISCSectionsChannel, AISCSectionsWF, AISCSectionsT, AISCSectionsL, AISCSections2L, AlumShapesL, AlumShapesChannel, AlumShapesCircular, AlumShapesRectangular, AlumShapesWF

site_class_options = ['A', 'B', 'C', 'D', 'E']

wf_section_sizes = AISCSectionsWF.objects().distinct(field="AISC_name")

rectangular_section_sizes = AISCSectionsRectangular.objects().distinct(field="AISC_name")

circular_section_sizes = AISCSectionsCircular.objects().distinct(field="AISC_name")

channel_section_sizes = AISCSectionsChannel.objects().distinct(field="AISC_name")

t_section_sizes = AISCSectionsT.objects().distinct(field="AISC_name")

angle_section_sizes = AISCSectionsL.objects().distinct(field="AISC_name")

doubleangle_section_sizes = AISCSections2L.objects().distinct(field="AISC_name")

alum_channel_sizes = AlumShapesChannel.objects().distinct(field="Size")

alum_angle_sizes = AlumShapesL.objects().distinct(field="Size")

alum_circular_sizes = AlumShapesCircular.objects().distinct(field="Size")

alum_rectangular_sizes = AlumShapesRectangular.objects().distinct(field="Name")

alum_wf_sizes = AlumShapesWF.objects().distinct(field="Size")
