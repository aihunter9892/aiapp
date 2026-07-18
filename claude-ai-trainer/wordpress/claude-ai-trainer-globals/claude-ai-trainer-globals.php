<?php
/**
 * Plugin Name: Claude AI Trainer — Globals
 * Description: Global content for claudeaitrainer.com — Claude model names, trainer count, contact details and the enquiry form as shortcodes — plus brand fonts/styling and a secure REST endpoint for remote page deployment.
 * Version: 1.1.0
 * Author: Claude AI Trainer
 */

if (!defined('ABSPATH')) exit;

/* ---------------------------------------------------------------------------
 * Brand fonts + polish CSS (makes the Elementor template look like the design)
 * ------------------------------------------------------------------------- */
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('cat-fonts',
        'https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap',
        array(), null);
    wp_register_style('cat-polish', false);
    wp_enqueue_style('cat-polish');
    wp_add_inline_style('cat-polish', '
        .elementor-section, .elementor-widget-text-editor, .elementor-widget-button a,
        .elementor-widget-icon-list .elementor-icon-list-text, .elementor-accordion,
        .cat-form { font-family: "Roboto", system-ui, sans-serif; }
        .elementor-heading-title, .elementor-counter-number-wrapper,
        .elementor-accordion .elementor-tab-title { font-family: "Space Grotesk", system-ui, sans-serif; letter-spacing: -0.01em; }
        .elementor-column > .elementor-widget-wrap { transition: transform .3s ease, box-shadow .3s ease; }
        .elementor-section .elementor-column:hover > .elementor-widget-wrap[style*="border"] { transform: translateY(-3px); }
        .elementor-widget-button .elementor-button { transition: transform .2s ease, box-shadow .2s ease; }
        .elementor-widget-button .elementor-button:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(217,119,87,.35); }
        .elementor-accordion .elementor-tab-title { font-size: 17px; }
        .elementor-accordion .elementor-tab-content { font-family: "Roboto", sans-serif; }
        a[href="#enquire"][style*="border-radius:999px"]:hover,
        a[style*="border-radius:999px"][style*="text-decoration:none"]:hover {
            border-color:#D97757 !important; color:#BD5D3A !important;
            transform: translateY(-1px); box-shadow: 0 6px 14px rgba(217,119,87,.18);
        }
        .elementor-page h1.entry-title, .elementor-page .page-title { display: none; }
    ');
});

/* ---------------------------------------------------------------------------
 * Remote deployment — secure REST endpoints (Application Password auth)
 *   GET  /wp-json/cat/v1/ping           -> connectivity + environment info
 *   POST /wp-json/cat/v1/import-page    -> create/update an Elementor page
 *        body: { "title": "Home", "slug": "home", "elementor": [...sections...],
 *                "set_front": true, "template": "elementor_header_footer" }
 * Both require an authenticated user with manage_options (use an
 * Application Password: WP Admin -> Users -> Profile -> Application Passwords).
 * ------------------------------------------------------------------------- */
add_action('rest_api_init', function () {
    register_rest_route('cat/v1', '/ping', array(
        'methods'  => 'GET',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function () {
            return array(
                'ok'        => true,
                'site'      => get_bloginfo('name'),
                'wp'        => get_bloginfo('version'),
                'elementor' => defined('ELEMENTOR_VERSION') ? ELEMENTOR_VERSION : null,
                'theme'     => wp_get_theme()->get('Name'),
                'plugin'    => '1.1.0',
            );
        },
    ));
    register_rest_route('cat/v1', '/import-page', array(
        'methods'  => 'POST',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => 'cat_rest_import_page',
    ));
});

function cat_rest_import_page(WP_REST_Request $req) {
    $title     = sanitize_text_field($req->get_param('title') ?: 'Home');
    $slug      = sanitize_title($req->get_param('slug') ?: $title);
    $elementor = $req->get_param('elementor');
    $template  = $req->get_param('template') ?: 'elementor_header_footer';
    if (!is_array($elementor)) {
        return new WP_Error('cat_bad_payload', 'Field "elementor" must be the Elementor content array.', array('status' => 400));
    }
    $existing = get_page_by_path($slug, OBJECT, 'page');
    $postarr = array(
        'post_title' => $title, 'post_name' => $slug,
        'post_type' => 'page', 'post_status' => 'publish', 'post_content' => '',
    );
    if ($existing) { $postarr['ID'] = $existing->ID; $id = wp_update_post($postarr, true); }
    else           { $id = wp_insert_post($postarr, true); }
    if (is_wp_error($id)) return $id;

    update_post_meta($id, '_elementor_data', wp_slash(wp_json_encode($elementor)));
    update_post_meta($id, '_elementor_edit_mode', 'builder');
    update_post_meta($id, '_elementor_template_type', 'wp-page');
    if (defined('ELEMENTOR_VERSION')) update_post_meta($id, '_elementor_version', ELEMENTOR_VERSION);
    if (in_array($template, array('elementor_canvas', 'elementor_header_footer'), true)) {
        update_post_meta($id, '_wp_page_template', $template);
    }
    delete_post_meta($id, '_elementor_css');
    if (class_exists('\\Elementor\\Plugin')) {
        \Elementor\Plugin::$instance->files_manager->clear_cache();
    }
    if ($req->get_param('set_front')) {
        update_option('show_on_front', 'page');
        update_option('page_on_front', $id);
    }
    return array('ok' => true, 'page_id' => $id, 'url' => get_permalink($id));
}

/* ---------------------------------------------------------------------------
 * Options (the single source of truth)
 * ------------------------------------------------------------------------- */
function cat_defaults() {
    return array(
        'model_flagship' => 'Claude Fable 5',
        'model_advanced' => 'Claude Opus 4.8',
        'model_balanced' => 'Claude Sonnet 5',
        'model_fast'     => 'Claude Haiku 4.5',
        'trainers'       => '300+',
        'email'          => 'reach@claudeaitrainer.com',
        'phone'          => '+91 81690 09783',
        'form_to'        => '', // blank = admin email
    );
}
function cat_get($key) {
    $opts = wp_parse_args((array) get_option('cat_globals', array()), cat_defaults());
    return isset($opts[$key]) ? $opts[$key] : '';
}

/* ---------------------------------------------------------------------------
 * Settings page: Settings → Claude AI Trainer
 * ------------------------------------------------------------------------- */
add_action('admin_menu', function () {
    add_options_page('Claude AI Trainer', 'Claude AI Trainer', 'manage_options', 'cat-globals', 'cat_settings_page');
});
add_action('admin_init', function () {
    register_setting('cat_globals_group', 'cat_globals', array(
        'sanitize_callback' => function ($in) {
            $out = array();
            foreach (cat_defaults() as $k => $v) {
                $out[$k] = isset($in[$k]) ? sanitize_text_field($in[$k]) : $v;
            }
            return $out;
        },
    ));
});
function cat_settings_page() {
    $labels = array(
        'model_flagship' => 'Flagship model (shortcode: [cat_model key="flagship"])',
        'model_advanced' => 'Advanced model ([cat_model key="advanced"])',
        'model_balanced' => 'Balanced model ([cat_model key="balanced"])',
        'model_fast'     => 'Fast model ([cat_model key="fast"])',
        'trainers'       => 'Trainers worldwide ([cat_trainers])',
        'email'          => 'Contact email ([cat_email])',
        'phone'          => 'Contact phone ([cat_phone])',
        'form_to'        => 'Form submissions go to (blank = admin email)',
    );
    ?>
    <div class="wrap"><h1>Claude AI Trainer — Global content</h1>
    <p>Change a value here and it updates <b>everywhere</b> the matching shortcode is used.
       Model list shortcode: <code>[cat_models]</code> · Enquiry form: <code>[cat_form]</code></p>
    <form method="post" action="options.php">
        <?php settings_fields('cat_globals_group'); ?>
        <table class="form-table">
        <?php foreach ($labels as $k => $label): ?>
            <tr><th scope="row"><label for="cat_<?php echo esc_attr($k); ?>"><?php echo esc_html($label); ?></label></th>
            <td><input class="regular-text" type="text" id="cat_<?php echo esc_attr($k); ?>"
                       name="cat_globals[<?php echo esc_attr($k); ?>]"
                       value="<?php echo esc_attr(cat_get($k)); ?>"></td></tr>
        <?php endforeach; ?>
        </table>
        <?php submit_button(); ?>
    </form></div>
    <?php
}

/* ---------------------------------------------------------------------------
 * Shortcodes — global text
 * ------------------------------------------------------------------------- */
add_shortcode('cat_model', function ($atts) {
    $a = shortcode_atts(array('key' => 'flagship'), $atts);
    return esc_html(cat_get('model_' . $a['key']));
});
add_shortcode('cat_models', function () {
    $m = array(cat_get('model_flagship'), cat_get('model_advanced'), cat_get('model_balanced'), cat_get('model_fast'));
    $m = array_filter(array_map('trim', $m));
    $last = array_pop($m);
    return esc_html($m ? implode(', ', $m) . ' and ' . $last : $last);
});
add_shortcode('cat_trainers', function () { return esc_html(cat_get('trainers')); });
add_shortcode('cat_email', function () {
    $e = cat_get('email');
    return '<a href="mailto:' . esc_attr($e) . '">' . esc_html($e) . '</a>';
});
add_shortcode('cat_phone', function () {
    $p = cat_get('phone');
    return '<a href="tel:' . esc_attr(preg_replace('/[^0-9+]/', '', $p)) . '">' . esc_html($p) . '</a>';
});

/* ---------------------------------------------------------------------------
 * Enquiry form — [cat_form]
 * ------------------------------------------------------------------------- */
add_shortcode('cat_form', function () {
    $sent = isset($_GET['cat_sent']) && $_GET['cat_sent'] === '1';
    ob_start(); ?>
    <div class="cat-form-wrap" id="enquire">
    <?php if ($sent): ?>
        <div class="cat-form-ok">✅ Thank you — your enquiry is in. We reply within one business day.</div>
    <?php endif; ?>
    <form class="cat-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
        <input type="hidden" name="action" value="cat_enquiry">
        <?php wp_nonce_field('cat_enquiry', 'cat_nonce'); ?>
        <input type="text" name="cat_hp" value="" style="position:absolute;left:-9999px" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="cat-row">
            <label>Name*<input type="text" name="cat_name" required></label>
            <label>Work email*<input type="email" name="cat_email" required></label>
        </div>
        <div class="cat-row">
            <label>Company<input type="text" name="cat_company"></label>
            <label>Phone / WhatsApp<input type="text" name="cat_phone"></label>
        </div>
        <div class="cat-row">
            <label>Location<input type="text" name="cat_location" placeholder="City, Country"></label>
            <label>Program
                <select name="cat_program">
                    <option>Corporate Training</option><option>Claude Masterclass</option>
                    <option>Claude for CXOs</option><option>Open Batches</option>
                    <option>Claude Code Bootcamp</option><option>AI Champions Program</option>
                    <option>Not sure yet</option>
                </select>
            </label>
        </div>
        <label>Tell us about your team &amp; goal<textarea name="cat_message" rows="4"></textarea></label>
        <button type="submit" class="cat-submit">Request a proposal</button>
    </form></div>
    <style>
      .cat-form{display:flex;flex-direction:column;gap:14px;max-width:640px}
      .cat-form .cat-row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
      @media(max-width:600px){.cat-form .cat-row{grid-template-columns:1fr}}
      .cat-form label{display:flex;flex-direction:column;gap:6px;font-weight:600;font-size:.9rem}
      .cat-form input,.cat-form select,.cat-form textarea{padding:11px 13px;border:1px solid #E4DFD4;border-radius:10px;font:inherit;background:#fff}
      .cat-submit{background:#D97757;color:#fff;border:0;border-radius:999px;padding:14px 30px;font-weight:700;font-size:1rem;cursor:pointer;align-self:flex-start}
      .cat-submit:hover{background:#BD5D3A}
      .cat-form-ok{background:#EAF7EF;border:1px solid #2E8B62;color:#1E5C41;padding:14px 18px;border-radius:12px;margin-bottom:16px;font-weight:600}
    </style>
    <?php return ob_get_clean();
});

function cat_handle_enquiry() {
    if (!isset($_POST['cat_nonce']) || !wp_verify_nonce($_POST['cat_nonce'], 'cat_enquiry')) wp_die('Invalid request.');
    if (!empty($_POST['cat_hp'])) { wp_safe_redirect(wp_get_referer() ?: home_url('/')); exit; } // honeypot
    $f = function ($k) { return sanitize_text_field(wp_unslash($_POST[$k] ?? '')); };
    $to = cat_get('form_to') ?: get_option('admin_email');
    $subject = 'Claude AI Trainer enquiry — ' . $f('cat_name') . ' (' . $f('cat_program') . ')';
    $body = "Name: {$f('cat_name')}\nEmail: {$f('cat_email')}\nCompany: {$f('cat_company')}\n"
          . "Phone: {$f('cat_phone')}\nLocation: {$f('cat_location')}\nProgram: {$f('cat_program')}\n\n"
          . "Message:\n" . sanitize_textarea_field(wp_unslash($_POST['cat_message'] ?? ''));
    wp_mail($to, $subject, $body, array('Reply-To: ' . $f('cat_email')));
    $back = wp_get_referer() ?: home_url('/');
    wp_safe_redirect(add_query_arg('cat_sent', '1', $back) . '#enquire'); exit;
}
add_action('admin_post_cat_enquiry', 'cat_handle_enquiry');
add_action('admin_post_nopriv_cat_enquiry', 'cat_handle_enquiry');
