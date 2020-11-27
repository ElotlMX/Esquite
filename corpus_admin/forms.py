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
    """**Clase encargada de generar de forma dinámica el formulario que
    permite modificar el nombre y el PDF de un documento existente**

    *Atributos*

    * placeholder: Variable que modifica el placeholder del input para el nuevo nombre del documento
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


class IndexConfigForm(forms.Form):
    """**Genera formulario para editar índice de elasticsearch**
    """
    ANALIZERS = [("sp", "spanish"), ("en", "english"), ("no", "Ninguno")]
    TYPES = [("kwd", "Palabras clave"), ("txt", "Texto")]
    index_name = forms.CharField(label='Índice',
                                 widget=forms.TextInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'En mínusculas'
                                 }),
                                 required=False)
    l1 = forms.CharField(label='L1',
                         widget=forms.TextInput(attrs={
                             'class': 'form-control'
                         }),
                         required=False)
    l1_analizers = forms.ChoiceField(label="Analizador L1",
                                    choices=ANALIZERS,
                                    widget=forms.Select(
                                        attrs={'class': 'form-control'}
                                    ))
    l2 = forms.CharField(label='L2',
                         widget=forms.TextInput(attrs={
                             'class': 'form-control'
                         }),
                         required=False)
    l2_analizers = forms.ChoiceField(label="Analizador L2",
                                    choices=ANALIZERS,
                                    widget=forms.Select(
                                        attrs={'class': 'form-control'}
                                    ))
    variants = forms.ChoiceField(label="Variantes", choices=TYPES,
                                 widget=forms.Select(
                                     attrs={'class': 'form-control'}),
                                 required=False)
    document_id = forms.ChoiceField(label="ID de documento", choices=TYPES,
                                 widget=forms.Select(
                                     attrs={'class': 'form-control'}),
                                 required=False)
    document_name = forms.ChoiceField(label="Nombre de documento", choices=TYPES,
                                 widget=forms.Select(
                                     attrs={'class': 'form-control'}),
                                 required=False)
    pdf_file = forms.ChoiceField(label="Archivo PDF", choices=TYPES,
                                 widget=forms.Select(
                                     attrs={'class': 'form-control'}),
                                 required=False)
    settings = forms.CharField(label='Settings',
                              widget=forms.Textarea(attrs={
                                  'class': 'form-control json-config',
                                  'placeholder': 'Something setting',
                                  'rows': 28,
                              }),
                              required=False)
    mapping = forms.CharField(label='Mapping',
                              widget=forms.Textarea(attrs={
                                  'class': 'form-control json-config',
                                  'placeholder': 'Something mapping',
                                  'rows': 28,
                              }),
                              required=False)
    autofill = forms.FileField(label="Autodetectar", required=False)

    autofill.widget.attrs.update({'hidden':''})

