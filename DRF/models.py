class CommanDocumentBase(AddCommonField):
    """
    Abstract base model for documents that stores common fields across various document types.
    This model includes all necessary fields that are common across documents.
    """
    id = models.BigAutoField(primary_key=True)
    document_category = models.ForeignKey(
        "Document_Category",
        related_name="document_category",
        on_delete=models.RESTRICT,
        null=False,
    )
    label_name = models.TextField(null=True)
    reference_id = models.IntegerField(null=True)
    reference_key = models.TextField(null=True)
    message = models.TextField(null=True)
    min_required_file = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)], null=True
    )
    max_required_file = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)], null=True
    )
    no_of_files = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)], null=True, default=0
    )
    required = models.BooleanField(null=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.RESTRICT, related_name="sub_categories"
    )
    period = models.IntegerField(null=True, blank=True)  # New field for period (e.g., duration)

    # New fields added to base model
    master_document = models.ForeignKey(
        "MasterDocument", on_delete=models.RESTRICT, null=True, related_name="master_document"
    )  # Foreign Key to MasterDocument
    doc_status = EnumField(enum=DocumentStatus, default=DocumentStatus.ENABLED)
    state = EnumField(enum=DocumentState, default=DocumentState.UPLOAD_PENDING) 

    reason = EnumField(enum=DocumentRejectionReason, null= True)
    type = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(99)], null=True
    )
    type_name = models.TextField(null=True)
    is_radio_status = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)], null=True
    )
    actions = ArrayField(models.IntegerField(), null=True)
    config = models.JSONField(default=dict, null=True, blank=True)
    required = models.BooleanField(null=True)
    on_list = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(99)], null=True
    )

    class Meta:
        abstract = True


class Document(CommanDocumentBase):
    """
    Represents a document that is associated with a specific document category, state, and status.
    This model inherits fields from the abstract CommanDocumentBase model.
    """
    class Meta:
        db_table = "dms_document"
        get_latest_by = "document_category"
        # unique_together = ('document_category_id', 'type_name','master_document_id') 

    def __str__(self):
        return self.label_name or f"Document {self.id}"