from common.common_utils import (
    generate_pre_signed_url_info,
    upload_file_to_pre_signed_url,
)
from django import forms


class PreSignedUrlAdminForm(forms.ModelForm):
    """
    Admin Form for handling pre-signed URL for image upload.
    Need to Define ImageField 'target_field_by_file_or_image_field' of key.

    Need to define Meta class with 'target_field_by_file_or_image_field' and 'upload_image_type'

    target_field_by_file_or_image_field key: The field name in the form for the image file upload.
    target_field_by_file_or_image_field value: The field name in the model for the image URL.
    upload_image_type: The type of image upload to folder of S3. Default is 'common'.
    boto_client: boto3 client for S3.
    upload_bucket_name: S3 bucket name.
    cloud_front_domain: CloudFront domain for the URL. Optional.

    examples:
    class XXXXForm(PreSignedUrlAdminForm):
        main_image_file = forms.ImageField(required=False)

        class Meta:
            model = XXXX
            fields = '__all__'
            target_field_by_file_or_image_field = {
                'main_image_file': 'main_image_url'
            }
            upload_image_type = 'xxxx_main_image'
            boto_client = boto3.client(...)
            upload_bucket_name = 'bucket_name'
            cloud_front_domain = 'cloud_front_domain'  # Optional, if you want to use
    """
    def __init__(self, *args, **kwargs):
        super(PreSignedUrlAdminForm, self).__init__(*args, **kwargs)
        target_field_by_file_or_image_field = self._get_target_field_by_file_or_image_field()
        if not target_field_by_file_or_image_field:
            raise Exception(
                'When using PreSignedUrlAdminForm need to define "Meta" class with "target_field_by_file_or_image_field."'
            )
        if not self._get_boto_client():
            raise Exception(
                'When using PreSignedUrlAdminForm need to define "Meta" class with "boto_client."'
            )
        if not self._get_upload_bucket_name():
            raise Exception(
                'When using PreSignedUrlAdminForm need to define "Meta" class with "upload_bucket_name."'
            )
        for key, target_field in target_field_by_file_or_image_field.items():
            if not isinstance(self.fields.get(key), (forms.ImageField, forms.FileField)):
                raise TypeError(f'Need to define "{key}" by ImageField in form.')
            if not hasattr(self.instance, target_field):
                raise AttributeError(f'Are you sure "{target_field}" is defined in model?')
            if not isinstance(self.base_fields.get(target_field), forms.Field):
                raise AttributeError(f'Not exists "{target_field}" in form.')
            if self.base_fields.get(target_field).required:
                raise AttributeError(f'Cannot set "{target_field}" as required in form. Please reset "required=False" in form.')

    def _get_meta(self):
        return getattr(self, 'Meta')

    def _get_target_field_by_file_or_image_field(self):
        return getattr(self._get_meta(), 'target_field_by_file_or_image_field', {})

    def _get_upload_image_type(self):
        return getattr(self._get_meta(), 'upload_image_type', 'common')

    def _get_boto_client(self):
        return getattr(self._get_meta(), 'boto_client', None)

    def _get_upload_bucket_name(self):
        return getattr(self._get_meta(), 'upload_bucket_name', None)

    def _get_cloud_front_domain(self):
        return getattr(self._get_meta(), 'cloud_front_domain', None)

    def save(self, commit=True):
        instance = super(PreSignedUrlAdminForm, self).save(commit=False)
        boto_client = self._get_boto_client()
        upload_bucket_name = self._get_upload_bucket_name()
        cloud_front_domain = self._get_cloud_front_domain()
        for key, value in self._get_target_field_by_file_or_image_field().items():
            if self.cleaned_data[key]:
                response = generate_pre_signed_url_info(
                    boto_client,
                    upload_bucket_name,
                    self.cleaned_data[key].name,
                    _type=self._get_upload_image_type(),
                    unique=str(instance.id) if instance.id else '0'
                )
                upload_file_to_pre_signed_url(
                    response['url'],
                    response['fields'],
                    self.cleaned_data[key].file,
                )
                if cloud_front_domain:
                    url = cloud_front_domain + '/'
                else:
                    url = response['url']
                setattr(instance, value, url + response['fields']['key'])
        if commit:
            instance.save()
        return instance
