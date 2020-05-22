from django import forms
from django.conf import settings
from .helpers import get_variants
# === Formulario de Búsqueda ===


class SearchPostForm(forms.Form):
    """**Clase encargada de generar de forma dinámica el formulario que permite
    hacer las búsquedas**

    *Atributos*

    * LANGUAGES: Lista de lenguas en las cuales se pueden hacer búsquedas con el formato `(KEY, VALUE)`
        :type: list
    * VARIANTS: Lista de variantes disponibles con el formato `(KEY, VALUE)`
        :type: list
    * search_placeholder: Variable que modifica el placeholder del elemento input para insertar el texto a buscar
        :type: str
    * variant_label: Variable que modifica la etiqueta de las variantes del corpus
        :type: str
    * idioma: Objeto de django forms que renderea un elemento ``<select>`` de ``html``
        :type: ``form.ChoiceField``
    * busqueda: Objeto de django forms que renderea un elemento ``<input>`` de html
        :type: ``form.CharField``
    * **variante** : Objeto de django forms que renderea un elemento ``<select>`` de ``html`` con multiples opciones
        :type: ``form.MultipleChoiceField``
    """
    # Lenguajes soportados
    LANGUAGES = [("L1", settings.L1), ("L2", settings.L2)]
    # Variantes actuales. Se requiere el formato de tupla (KEY, VALUE)
    variantes = get_variants()
    variants_attrs = {'class': 'form-control'}
    if variantes['status'] == 'success':
        del variantes['status']
        if len(variantes):
            VARIANTS = variantes.items()
        else:
            VARIANTS = []
            variants_attrs['disabled'] = True
    elif variantes['status'] == 'error':
        VARIANTS = []
        variants_attrs['disabled'] = True
    search_placeholder = 'Palabra o frase a buscar'
    variant_label = 'Resultados por variante (opcional)'
    idioma = forms.ChoiceField(choices=LANGUAGES,
                               widget=forms.Select(
                                   attrs={'class': 'form-control'}))
    busqueda = forms.CharField(label="Búsqueda",
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control',
                                          'placeholder': search_placeholder}))
    variante = forms.MultipleChoiceField(label=variant_label,
                                         choices=VARIANTS,
                                         widget=forms.SelectMultiple(
                                             attrs={'class': 'form-control'}),
                                         required=False)
