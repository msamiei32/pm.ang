﻿"use strict";

// Class definition
var KTModalAddAddress = function () {
    var submitButton;
    var cancelButton;
	var closeButton;
    var validator;
    var form;
    var modal;

    // Init form inputs
    var handleForm = function () {
        // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		validator = FormValidation.formValidation(
			form,
			{
				fields: {
                    'name': {
						validators: {
							notEmpty: {
								message: 'Address name is required'
							}
						}
					},
					'country': {
						validators: {
							notEmpty: {
								message: 'Country is required'
							}
						}
					},
					'address1': {
						validators: {
							notEmpty: {
								message: 'Address 1 is required'
							}
						}
					},
					'city': {
						validators: {
							notEmpty: {
								message: 'City is required'
							}
						}
					},
					'state': {
						validators: {
							notEmpty: {
								message: 'State is required'
							}
						}
					},
					'postcode': {
						validators: {
							notEmpty: {
								message: 'Postcode is required'
							}
						}
					}
				},
				plugins: {
					trigger: new FormValidation.plugins.Trigger(),
					bootstrap: new FormValidation.plugins.Bootstrap5({
						rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
					})
				}
			}
		);

		// Revalidate country field. For more info, plase visit the official plugin site: https://select2.org/
        $(form.querySelector('[name="country"]')).on('change', function() {
            // Revalidate the field when an option is chosen
            validator.revalidateField('country');
        });

		// Action buttons
		submitButton.addEventListener('click', function (e) {
			e.preventDefault();

			// Validate form before submit
			if (validator) {
				validator.validate().then(function (status) {
					console.log('validated!');

					if (status == 'Valid') {
						submitButton.setAttribute('data-kt-indicator', 'on');

						// Disable submit button whilst loading
						submitButton.disabled = true;

						setTimeout(function() {
							submitButton.removeAttribute('data-kt-indicator');
							
							Swal.fire({
								text: "فرم با موفقیت ارسال شد!",
								icon: "success",
								buttonsStyling: false,
								confirmButtonText: "باشه فهمیدم!",
								customClass: {
									confirmButton: "btn btn-primary"
								}
							}).then(function (result) {
								if (result.isConfirmed) {
									// Hide modal
									modal.hide();

									// Enable submit button after loading
									submitButton.disabled = false;
								}
							});							
						}, 2000);   						
					} else {
						Swal.fire({
							text: "متأسفیم ، به نظر می رسد برخی خطاها شناسایی شده است ، لطفاً دوباره امتحان کنید.",
							icon: "error",
							buttonsStyling: false,
							confirmButtonText: "باشه فهمیدم!",
							customClass: {
								confirmButton: "btn btn-primary"
							}
						});
					}
				});
			}
		});

        cancelButton.addEventListener('click', function (e) {
            e.preventDefault();

            Swal.fire({
                text: "آیا مطمئن هستید که می خواهید لغو کنید؟?",
                icon: "warning",
                showCancelButton: true,
                buttonsStyling: false,
                confirmButtonText: "بله ، آن را لغو کنید!",
                cancelButtonText: "خیر",
                customClass: {
                    confirmButton: "btn btn-primary",
                    cancelButton: "btn btn-active-light"
                }
            }).then(function (result) {
                if (result.value) {
                    form.reset(); // Reset form	
                    modal.hide(); // Hide modal				
                } else if (result.dismiss === 'cancel') {
                    Swal.fire({
                        text: "فرم شما لغو نشده است !.",
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "باشه فهمیدم!",
                        customClass: {
                            confirmButton: "btn btn-primary",
                        }
                    });
                }
            });
        });

		closeButton.addEventListener('click', function(e){
			e.preventDefault();

            Swal.fire({
                text: "آیا مطمئن هستید که می خواهید لغو کنید؟?",
                icon: "warning",
                showCancelButton: true,
                buttonsStyling: false,
                confirmButtonText: "بله ، آن را لغو کنید!",
                cancelButtonText: "خیر",
                customClass: {
                    confirmButton: "btn btn-primary",
                    cancelButton: "btn btn-active-light"
                }
            }).then(function (result) {
                if (result.value) {
                    form.reset(); // Reset form	
                    modal.hide(); // Hide modal				
                } else if (result.dismiss === 'cancel') {
                    Swal.fire({
                        text: "فرم شما لغو نشده است !.",
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "باشه فهمیدم!",
                        customClass: {
                            confirmButton: "btn btn-primary",
                        }
                    });
                }
            });
		})
    }

    return {
        // Public functions
        init: function () {
            // Elements
            modal = new bootstrap.Modal(document.querySelector('#kt_modal_add_address'));

            form = document.querySelector('#kt_modal_add_address_form');
            submitButton = form.querySelector('#kt_modal_add_address_submit');
            cancelButton = form.querySelector('#kt_modal_add_address_cancel');
			closeButton = form.querySelector('#kt_modal_add_address_close');

            handleForm();
        }
    };
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
	KTModalAddAddress.init();
});