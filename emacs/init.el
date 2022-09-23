;;; build.el --- Minimal emacs installation to build the website -*- lexical-binding: t -*-
;; Authors: Bruno Henriques <4727729+bphenriques@users.noreply.github.com>
;; Modified from: https://github.com/bphenriques/knowledge-base/blob/master/tools/init.el

;;; Commentary:
;;; - Requires BASE_DIR environment variable
;;
;; Notes:
;; * This is not a package.
;;; Code:

(require 'subr-x)

; (toggle-debug-on-error)                                       ;; Show debug information as soon as error occurs.
(setq
 make-backup-files nil                                        ;; Disable "<file>~" backups.
)

(defconst base-dir
  (let* ((env-key "BASE_DIR")
         (env-value (getenv env-key)))
    (if (and env-value (file-directory-p env-value))
        env-value
      (error (format "%s is not set or is not an existing directory (%s)" env-key env-value)))))

;;;
;;; Setup packages using straight.el: https://github.com/raxod502/straight.el
;;;
;;; Leads to better reproducible builds as the versions are pinned.
(defvar bootstrap-version)
(let ((bootstrap-file
       (expand-file-name "straight/repos/straight.el/bootstrap.el" user-emacs-directory))
      (bootstrap-version 5))
  (unless (file-exists-p bootstrap-file)
    (with-current-buffer
        (url-retrieve-synchronously
         "https://raw.githubusercontent.com/raxod502/straight.el/develop/install.el"
         'silent 'inhibit-cookies)
      (goto-char (point-max))
      (eval-print-last-sexp)))
  (load bootstrap-file nil 'nomessage))

(setq straight-use-package-by-default t)
(straight-use-package 'use-package)

;;;
;;; Setup packages
;;;

(use-package ox-hugo
  :straight (:type git :host github :repo "kaushalmodi/ox-hugo" :nonrecursive t))

(use-package citeproc
  :straight (:type git :host github :repo "andras-simonyi/citeproc-el" :nonrecursive t))

(setf org-hugo-base-dir base-dir)

; Disable auto-inserting References section heading.
; https://ox-hugo.scripter.co/doc/org-cite-citations/#org-radio--CSL-formatted-exports
(with-eval-after-load 'ox-hugo
  (plist-put org-hugo-citations-plist :bibliography-section-heading ""))

; Auto-prefix type (figure/table) of links.
; https://ox-hugo.scripter.co/doc/linking-numbered-elements/#fnref:1
(with-eval-after-load 'ox-hugo
  (setq org-hugo-link-desc-insert-type t))


;;;
;;; Public functions
;;;

(defun build/export-all ()
  "Export all org-files (including nested) under base-org-files."
  (let ((search-path (file-name-as-directory base-dir)))
    (message (format "[build] Looking for files at %s" search-path))
    (dolist (org-file (directory-files-recursively search-path "\.org$" nil (lambda (x) (not (string-match-p "emacs" x)))))
      (with-current-buffer (find-file org-file)
   (message (format "[build] Exporting %s" org-file))
   (org-hugo-export-wim-to-md :all-subtrees nil nil nil)))
    (message "Done!")))

(provide 'build/export-all)

;;; init.el ends here
