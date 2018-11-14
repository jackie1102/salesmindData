$(function () {
    var error_position = false;
    var error_addr = false;
    var error_industry = false;
    var error_update = false;
    var error_status = false;
    $('#position1').blur(function () {
        check_position1(false)
    });
    $('#addr1').blur(function () {
        check_addr1(false)
    });
    $('#industry1').blur(function () {
        check_industry1(false)
    });
    $('#update1').blur(function () {
        check_update1(false)
    });
    $('#status1').blur(function () {
        check_status1(false)
    });
    $('#position2').blur(function () {
        check_position2(false)
    });
    $('#addr2').blur(function () {
        check_addr2(false)
    });
    $('#industry2').blur(function () {
        check_industry2(false)
    });
    $('#update2').blur(function () {
        check_update2(false)
    });
    $('#status2').blur(function () {
        check_status2(false)
    });

    function check_position1(async) {
        var position = $('#position1').val();
        if (position == '') {
            $('#position1').next().html('').hide();
            error_position = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_position/?position=' + position,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#position1').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_position = true
                }
                else {
                    $('#position1').next().html('').hide();
                    error_position = false
                }
            }
        })
    }

    function check_position2(async) {
        var position = $('#position2').val();
        if (position == '') {
            $('#position2').next().html('').hide();
            error_position = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_position/?position=' + position,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#position2').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_position = true
                }
                else {
                    $('#position2').next().html('').hide();
                    error_position = false
                }
            }
        })
    }

    function check_addr1(async) {
        var addr = $('#addr1').val();
        if (addr == '') {
            $('#addr1').next().html('').hide();
            error_addr = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_addr/?addr=' + addr,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#addr1').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_addr = true
                }
                else {
                    $('#addr1').next().html('').hide();
                    error_addr = false
                }
            }
        })
    }

    function check_addr2(async) {
        var addr = $('#addr2').val();
        if (addr == '') {
            $('#addr2').next().html('').hide();
            error_addr = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_addr/?addr=' + addr,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#addr2').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_addr = true
                }
                else {
                    $('#addr2').next().html('').hide();
                    error_addr = false
                }
            }
        })
    }

    function check_industry1(async) {
        var industry = $('#industry1').val();
        if (industry == '') {
            $('#industry1').next().html('').hide();
            error_industry = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_industry/?industry=' + industry,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#industry1').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_industry = true
                }
                else {
                    $('#industry1').next().html('').hide();
                    error_industry = false
                }
            }
        })
    }

    function check_industry2(async) {
        var industry = $('#industry2').val();
        if (industry == '') {
            $('#industry2').next().html('').hide();
            error_industry = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_industry/?industry=' + industry,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#industry2').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_industry = true
                }
                else {
                    $('#industry2').next().html('').hide();
                    error_industry = false
                }
            }
        })
    }
    function check_update1(async) {
        var update = $('#update1').val();
        if (update == '') {
            $('#update1').next().html('').hide();
            error_update = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_update/?update=' + update,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#update1').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_update = true
                }
                else {
                    $('#update1').next().html('').hide();
                    error_update = false
                }
            }
        })
    }
    function check_update2(async) {
        var update = $('#update2').val();
        if (update == '') {
            $('#update2').next().html('').hide();
            error_update = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_update/?update=' + update,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#update2').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_update = true
                }
                else {
                    $('#update2').next().html('').hide();
                    error_update = false
                }
            }
        })
    }
    function check_status1(async) {
        var status = $('#status1').val();
        if (status == '') {
            $('#status1').next().html('').hide();
            error_status = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_status/?status=' + status,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#status1').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_status = true
                }
                else {
                    $('#status1').next().html('').hide();
                    error_status = false
                }
            }
        })
    }
    function check_status2(async) {
        var status = $('#status2').val();
        if (status == '') {
            $('#status2').next().html('').hide();
            error_status = false;
            return
        }
        $.ajax({
            'url': '/spider/check_job_status/?status=' + status,
            'async': async,
            'success': function (data) {
                if (data.errId != 0) {
                    $('#status2').next().html('&nbsp;&nbsp;&nbsp;' + data.errMsg).show();
                    error_status = true
                }
                else {
                    $('#status2').next().html('').hide();
                    error_status = false
                }
            }
        })
    }
});