class HeadDocumentSerializerV2(DynamicFieldsModelSerializer):
    id = KuhooIntegerField(
        label="Document Id", required=False, restrict_roles=[CUSTOMER,VERIF_SERVICE,TE, PARTNER,COAPP_LINK_ROLE, CM,BM,CO, CC,LOS_SERVICE, RM, DV]
    )
    label_name = KuhooCharField(required=False, store_lower=False, restrict_roles=[DV,CM,CO,CC],read_only = True)
    reference_id = KuhooIntegerField(required=False, allow_null=True)
    reference_key = KuhooCharField(required=False, store_lower=False, allow_null=True)
    message = KuhooCharField(allow_blank=True, allow_null=True, required=False, restrict_roles=[DV,CM,CO,CC,VERIF_SERVICE, LOS_SERVICE])
    no_of_files = KuhooIntegerField(required=False, default=0, read_only = True)
    required = KuhooBooleanField(required=False)
    document_type_id = KuhooIntegerField(source='master_document.id', required = False)    
    doc_status = EnumField(enum=DocumentStatus, default= DocumentStatus.ENABLED, label_name= 'label', required=False)
    state = EnumField(enum=DocumentState, default= DocumentState.UPLOAD_PENDING, label_name= 'label',read_only = True)
    reason = EnumField(enum=DocumentRejectionReason, label_name= 'label', required= False,read_only = True)
    type = KuhooCharField(source='master_document.type',read_only = True)
    type_name = KuhooCharField(
        allow_blank=True,
        store_lower=False,
        allow_null=True,
        required=False,
        restrict_roles=[CUSTOMER, PARTNER,TE, LOS_SERVICE,CM,CC,VERIF_SERVICE,COAPP_LINK_ROLE,CO, BM,RM, DV]
    )
    is_radio_status = KuhooCharField(required = False, read_only = True)
    actions = KuhooListField(required=False)
    document_category = KuhooIntegerField(source='document_category.id', required = False, read_only = True)    
    class Meta:
        model = Document
        exclude = (
            "status",
            "creation_date",
            "creation_by",
            "updation_date",
            "updation_by",
        )
        list_serializer_class = IsActiveListSerializer
    from document.helper_func import add_document_label_message
    @add_document_label_message
    def add_label_text(self,obj):
        return obj
    
    def validate_document_type_id(self,value):
        if not MasterDocument.objects.filter(id = value, status = STATUS_ACTIVE).exists():
            raise CustomExceptionHandler(Statuses.document_type_not_present_in_system)
    def refine_validated_data(self,master_document, category_object):
        if master_document.type == DEFAULT_DOCUMENT:
            self.validated_data["label_name"] = " ".join(word.capitalize() for word in self.validated_data.get("type_name").split("_"))
        else:
            self.validated_data["label_name"] = master_document.label_name
        if self.validated_data.get("period"):
            self.validated_data["label_name"] = self._write_label_name(
                self.validated_data["label_name"], self.validated_data["period"])
        self.validated_data["master_document"] = master_document
        self.validated_data["document_category"] = category_object
        if "required" not in self.validated_data.keys() and "id" not in self.validated_data.keys():
            self.validated_data["required"] = True if master_document.mandatory == MandatoryChoice.REQUIRED else False
    
    def validate_actions(self, value):
        if not value:
            return value
        temp_list = []
        for i in value:
            temp_list.append(common_checking_and_passing_value_from_list_dict(
            i, DocDictionary.actions, Statuses.actions_not_responding_properly
        ))
        return temp_list
    
    def _write_label_name(self, name, period):
        trace_log("Writing label name.")
        if period:
            years, months = divmod(period, 12)
            if months == 0:
                name = (
                    f"{years} Year {name}"
                    if years == 1
                    else f"{years} Years {name}"
                )
            elif years == 0:
                name = (
                    f"{months} Month {name}"
                    if months == 1
                    else f"{months} Months {name}"
                )
            else:
                name = (
                    f"{years} Year and {months} Month {name}"
                    if years <= 1 and months <= 1
                    else f"{years} Years and {months} Months {name}"
                )
            trace_log(f"Updated label name: {name}")
        return name
    
    def _allow_doc_state_change(self, instance):
        if not instance.parent and not instance.master_document.is_sub_category:
            if instance.state in [DocumentState.UPLOAD_PENDING,DocumentState.REJECTED]:
                return True
        if instance.master_document.is_sub_category:
            totel_obj = Document.objects.filter(parent = instance.parent,status = STATUS_ACTIVE).count()
            rejected = Document.objects.filter(parent = instance.parent, status = STATUS_ACTIVE, state = DocumentState.REJECTED).count()
            upload_pending = Document.objects.filter(parent = instance.parent, status = STATUS_ACTIVE, state = DocumentState.UPLOAD_PENDING).count()
            return totel_obj == rejected+upload_pending
        return False
            
    
    def _extract_info_from_mastar(self,master_instance,obj):
        obj["min_required_file"] = master_instance.min_no_of_files
        obj["max_required_file"] = master_instance.max_no_of_files
        obj["is_sub_category"] = master_instance.is_sub_category
        obj["reference_key"] = master_instance.reference_data
        

    def to_representation(self, instance):
        obj =  super().to_representation(instance)
        obj["allow_doc_status_change"] = self._allow_doc_state_change(instance)
        obj["is_delete_allowed"] = True if obj["type"] == "default" and instance.document_category.master_category.type in DocDictionary.category_document_deletion_allowed and instance.state != DocDictionary.document_state[APPROVED] else False
        self.add_label_text(obj)
        self._extract_info_from_mastar(instance.master_document, obj)
        return obj