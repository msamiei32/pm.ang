﻿"use strict";

// Class definition
var KTSubscriptionsExport = function () {
    var element;
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
                    'date': {
                        validators: {
                            notEmpty: {
                                message: 'Date range is required'
                            }
                        }
                    },
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

                        setTimeout(function () {
                            submitButton.removeAttribute('data-kt-indicator');

                            Swal.fire({
                                text: "Customer list has been successfully exported!",
                                icon: "success",
                                buttonsStyling: false,
                                confirmButtonText: "باشه فهمیدم!",
                                customClass: {
                                    confirmButton: "btn btn-primary"
                                }
                            }).then(function (result) {
                                if (result.isConfirmed) {
                                    modal.hide();

                                    // Enable submit button after loading
                                    submitButton.disabled = false;
                                }
                            });

                            //form.submit(); // Submit form
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

        closeButton.addEventListener('click', function (e) {
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
    }

    var initForm = function () {
        const datepicker = form.querySelector("[name=date]");

        // Handle datepicker range -- For more info on flatpickr plugin, please visit: https://flatpickr.js.org/
        $(datepicker).flatpickr({
            altInput: true,
            altFormat: "F j, Y",
            dateFormat: "Y-m-d",
            mode: "range"
        });
    }

    return {
        // Public functions
        init: function () {
            // Elements
            element = document.querySelector('#kt_subscriptions_export_modal');
            modal = new bootstrap.Modal(element);

            form = document.querySelector('#kt_subscriptions_export_form');
            submitButton = form.querySelector('#kt_subscriptions_export_submit');
            cancelButton = form.querySelector('#kt_subscriptions_export_cancel');
            closeButton = element.querySelector('#kt_subscriptions_export_close');

            handleForm();
            initForm();
        }
    };
}();

// On document ready
KTUtil.onDOMContentLoaded(function () {
    KTSubscriptionsExport.init();
});