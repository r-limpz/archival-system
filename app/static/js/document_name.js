let documentDetails = {
    academicYear: '',
    college: '',
    course: '',
    yearLevel: '',
    section: '',
    subjectName: '',
    subjectType: '',
    semester: ''
};

function updateDocumentName() {
    let allEmpty = Object.values(documentDetails).every(function (value) {
        return value.trim() === '';
    });

    if (allEmpty) {
        $("#document_filename").val("");
    } else {
        let colcourse = documentDetails.college && documentDetails.course
            ? documentDetails.college + '-' + documentDetails.course
            : (documentDetails.college || documentDetails.course);

        let year_level = documentDetails.yearLevel !== "0" && documentDetails.section
            ? documentDetails.yearLevel + documentDetails.section
            : (documentDetails.yearLevel !== "0" && documentDetails.section === "")
                ? documentDetails.yearLevel
                : '';

        let subject = documentDetails.subjectName && documentDetails.subjectType
            ? documentDetails.subjectName + (documentDetails.subjectType === "1"
                ? '_lect'
                : documentDetails.subjectType === "2"
                    ? '_lab'
                    : '')
            : '';

        let academic_year = documentDetails.semester !== "0" && documentDetails.academicYear
            ? documentDetails.semester + '_' + documentDetails.academicYear
            : documentDetails.semester !== "0"
                ? documentDetails.semester
                : documentDetails.academicYear || '';


        let combination1 = colcourse && year_level
            ? colcourse + '-' + year_level
            : colcourse && year_level === ""
                ? colcourse
                : colcourse === "" && year_level
                    ? year_level
                    : '';

        let combination2 = subject && academic_year
            ? subject + '_' + academic_year
            : subject === "" && academic_year
                ? academic_year
                : subject && academic_year === ""
                    ? subject
                    : '';

        let doc_name = combination1 && combination2
            ? combination1 + '_' + combination2
            : combination1 || combination2 || '';

        $("#document_filename").val(doc_name);
    }
}

$("#document_college, #document_course, #document_yearLevel, #document_subject_type, #document_semester").change(function () {
    updateObject();
    updateDocumentName();
});

$("#course_section, #document_subject_name, #starting_year, #ending_year").on('input', function () {
    updateObject();
    updateDocumentName();
});

function updateObject() {
    documentDetails = {
        academicYear: $('#starting_year').val() && $('#ending_year').val() ? $('#starting_year').val() + '-' + $('#ending_year').val() : '',
        college: $('#document_college option:selected').text(),
        course: $('#document_course option:selected').text(),
        yearLevel: $('#document_yearLevel option:selected').val(),
        section: $('#course_section').val().replace(/\s+/g, ''),
        subjectName: $('#document_subject_name').val(),
        subjectType: $('#document_subject_type option:selected').val(),
        semester: $('#document_semester option:selected').text().replace(/\s+/g, ''),
    };
}
