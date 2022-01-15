from django import forms


class NewDocumentForm(forms.Form):
    """**Clase encargada de generar de forma dinámica el formulario
    que permite cargar nuevos documentos al corpus**

    *Atributos*

    * VARIANTS: Lista de variantes disponibles con el formato ``(KEY, VALUE)``
        :type: list
    * nombre: Objeto de django forms que renderea un elemento input de html
        :type: ``form.CharField``
    * csv: Objeto de django forms que renderea un elemento input de html
        :type: ``form.FileField``
    * pdf: Objeto de django forms que renderea un elemento input de html
        :type: ``form.FileField``
    """
    nombre = forms.CharField(label='Nombre',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': 'Nombre del documento'})
                             )
    csv = forms.FileField(label='CSV')
    pdf = forms.FileField(label='PDF')


class AddDocumentDataForm(forms.Form):
    """**Clase encargada de generar de forma dinámica el formulario que
    permite agregar nuevos renglones a un documento particular del
    corpus**

    *Atributos*

    * csv: Objeto de django forms que renderea un elemento input de html
        :type: ``form.FileField``
    """
    csv = forms.FileField(label='CSV')


class DocumentEditForm(forms.Form):
    """**Clase encargada de generar de forma dinámica el formulario
    que permite modificar el nombre y el PDF de un documento existente**

    *Atributos*

    * placeholder: Variable que modifica el placeholder del input para
        el nuevo nombre del documento
        :type: str
    * nombre: Objeto de django forms que renderea un elemento input de html
        :type: ``form.CharField``
    * pdf: Objeto de django forms que renderea un elemento input de html
        :type: ``form.FileField``
    """
    placeholder = "Ingresa el nuevo nombre del documento"
    nombre = forms.CharField(label='Nombre',
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': placeholder}),
                             required=False)
    pdf = forms.FileField(label="PDF", required=False)

