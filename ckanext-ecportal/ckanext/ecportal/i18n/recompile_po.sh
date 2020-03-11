#!/bin/bash

cd ${CKAN_FOLDER}/ckanext-ecportal/ckanext/ecportal/i18n
LANGS=('en' 'fr' 'de' 'it' 'es' 'pl' 'ga' 'lv' 'bg' 'lt' 'cs' 'da' 'nl' 'et' 'fi' 'el' 'hu' 'mt' 'pt' 'ro' 'sk' 'sl' 'sv' 'hr' 'zh')
for lang in ${LANGS[@]}; do
	msgfmt -o ./${lang}/LC_MESSAGES/ckan.mo ./${lang}/LC_MESSAGES/ckan.po
done

echo "PO files compiled"
