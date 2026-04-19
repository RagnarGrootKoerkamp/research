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
(straight-use-package 'org)

;;;
;;; Setup packages
;;;

(use-package ox-hugo
  :straight (:type git :host github :repo "kaushalmodi/ox-hugo" :nonrecursive t))

(use-package citeproc
  :straight (:type git :host github :repo "andras-simonyi/citeproc-el" :nonrecursive t))

(use-package ox-reveal
  :straight (:type git :host github :repo "yjwen/org-reveal" :files ("*.el")))

(require 'ox-reveal)
(setq org-reveal-root "https://cdn.jsdelivr.net/npm/reveal.js")
(setq org-reveal-hlevel 0)

;; Fix: org-special-block-extras wraps custom block output in #+begin_export reveal,
;; but ox-reveal inherits org-html-export-block which only handles "HTML" type blocks.
;; "REVEAL" type blocks are silently dropped, so the <div> wrappers disappear and
;; only the raw text content survives as a plain paragraph.
(defun my/org-reveal-export-block (export-block _contents _info)
  "Pass through HTML and REVEAL type export blocks as raw HTML."
  (when (member (org-element-property :type export-block) '("HTML" "REVEAL"))
    (org-remove-indentation (org-element-property :value export-block))))
(let ((backend (org-export-get-backend 'reveal)))
  (unless (assq 'export-block (org-export-backend-transcoders backend))
    (setf (org-export-backend-transcoders backend)
          (cons '(export-block . my/org-reveal-export-block)
                (org-export-backend-transcoders backend)))))

;; Fix: org-reveal-link blindly rewrites ALL <a href="#"> → <a href="#/slide-">,
;; including our custom [[dfn:*]] links which already output the correct href.
;; For our special-block link types, call org-html-link directly to bypass rewriting.
(defvar my/special-block-link-types '("dfn" "thm" "lem" "prob" "conj" "alg")
  "Link types registered by defspeciallink; exempt from org-reveal-link's #/slide- rewrite.")
(advice-add 'org-reveal-link :around
            (lambda (orig-fn link desc info)
              (if (member (org-element-property :type link) my/special-block-link-types)
                  (org-html-link link desc info)
                (funcall orig-fn link desc info))))

;; Support #+reveal_export_file_name as a reveal-specific output path,
;; so it doesn't conflict with #+export_file_name used by other backends.
;; Resolves to an absolute path and creates parent directories as needed.
(advice-add 'org-reveal-export-to-html :around
            (lambda (orig-fn &rest args)
              (let ((reveal-file
                     (save-excursion
                       (goto-char (point-min))
                       (when (re-search-forward
                              "^[ \t]*#\\+REVEAL_EXPORT_FILE_NAME:[ \t]+\\(\\S-+\\)" nil t)
                         (expand-file-name (match-string-no-properties 1)
                                           (file-name-directory buffer-file-name))))))
                (if reveal-file
                    (progn
                      (make-directory (file-name-directory reveal-file) t)
                      (cl-letf (((symbol-function 'org-export-output-file-name)
                                 (lambda (_ext &rest _) reveal-file)))
                        (apply orig-fn args)))
                  (apply orig-fn args)))))

(setf org-hugo-base-dir base-dir)

                                        ; Disable auto-inserting References section heading.
                                        ; https://ox-hugo.scripter.co/doc/org-cite-citations/#org-radio--CSL-formatted-exports
                                        ; https://github.com/kaushalmodi/ox-hugo/issues/679
;; (with-eval-after-load 'ox-hugo
;;   (plist-put org-hugo-citations-plist :bibliography-section-heading ""))

                                        ; Auto-prefix type (figure/table) of links.
                                        ; https://ox-hugo.scripter.co/doc/linking-numbered-elements/#fnref:1
(setq org-hugo-link-desc-insert-type t)

                                        ; Use CSL by default
(setq org-cite-export-processors '((t csl)))

(setq org-cite-global-bibliography (list (expand-file-name "references.bib")))
(setq org-hugo-base-dir (expand-file-name "."))

(setq user-full-name "Ragnar Groot Koerkamp")

;;;
;;; org-special-blocks-extra
;;;
(use-package org-special-block-extras
  :ensure t)

;; Do not inject tooltipster CSS/JS into every slide's <head>.
(setq org-special-block-add-html-extra nil)

(org-mode)
;; (org-special-block-extras-mode 1)

(defmacro special-block-labels-push (prefix label)
  (let ((labels (format "special-block-%s-labels" prefix))
        (labels-cdr (format "special-block-%s-labels-cdr" prefix)))
    `(let ((label (list (format "%s" ,label))))
       (setq ,(intern labels-cdr)
             (if ,(intern labels-cdr)
                 (setcdr ,(intern labels-cdr) label)
               (setq ,(intern labels) label))))))

(defmacro defspeciallink (name display-name prefix)
  `(progn
     (defvar ,(intern (format "special-block-%s-labels" prefix)) '()) ; to store this theorem labels
     (defvar ,(intern (format "special-block-%s-labels-cdr" prefix)) nil)

     (org-defblock ,prefix (ref nil) ()
                   ,(format "Reference a %s special block." name)
                   (let* ((num (1+ (cl-position (format "%s" ref)
                                                ,(intern (format "special-block-%s-labels" prefix))
                                                :test 'equal))))
                     (cond
                      ((org-export-derived-backend-p org-export-current-backend 'latex)
                       (format ,(format "\\ref{%s:%%s}" prefix) ref))
                      ((org-export-derived-backend-p org-export-current-backend 'reveal)
                       (format ,(format "<a href=\"#%s:%%s\" onclick=\"event.preventDefault();var e=document.getElementById('%s:%%s');Reveal.slide(Reveal.getIndices(e).h,Reveal.getIndices(e).v);\">%s %%d</a>"
                                        prefix prefix display-name)
                               ref ref num))
                      ((org-export-derived-backend-p org-export-current-backend 'html)
                       (format ,(format "<a href=\"#%s:%%s\">%s %%d</a>" prefix display-name)
                               ref num)))))))

(defmacro deftheorem (name display-name prefix)
  "Defines a new theorem type called NAME (rendered as DISPLAY-NAME in HTML) which labels start with PREFIX.
Usage:
,#+BEGIN_name Title :label lbl
....
,#+END_name
As can be seen in [[prefix:lbl]]
                "
  `(progn
     (defspeciallink ,name ,display-name ,prefix)

     (org-defblock ,name (title "" label nil unnumbered nil skip nil)
                   ,(format "Define %s special block." name)
                   (unless unnumbered (special-block-labels-push ,prefix label)) ; add label to list
                   (cond
                    ((org-export-derived-backend-p org-export-current-backend 'latex)
                     (concat ,(format "\\begin{%s" name) (when unnumbered "*") "}"
                             (when (org-string-nw-p title) (format "[%s]" title))
                             (format ,(format "\\label{%s:%%s}" prefix) (or label ""))
                             (format "\n%s" contents)
                             ,(format "\\end{%s" name) (when unnumbered "*") "}"))
                    ((and skip (org-export-derived-backend-p org-export-current-backend 'reveal))
                     "")
                    ((org-export-derived-backend-p org-export-current-backend 'html)
                     (format
                      (concat ,(format "<div id=\"%s:%%s\" class=\"special-block %s\"><span class=\"special-block-title\"><span class=\"special-block-number\">%s" prefix name display-name)
                              (unless unnumbered (format " %d" (length ,(intern (format "special-block-%s-labels" prefix)))))
                              "</span>"
                              (when (org-string-nw-p title) " <span class=\"special-block-name\">") "%s" (when (org-string-nw-p title) "</span>") ".</span>"
                              ,(format "%%s</div>"))
                      (or label "") (or (org-string-nw-p title) "") contents))
                    )
                   )))

(deftheorem definition "Definition" dfn)
(deftheorem newdefinition "Definition" dfn)
(deftheorem theorem "Theorem" thm)
(deftheorem mytheorem "Theorem" thm)
(deftheorem lemma "Lemma" lem)
(deftheorem problem "Problem" prob)
(deftheorem openproblem "Open problem" prob)
(deftheorem conjecture "Conjecture" conj)
(deftheorem algorithm "Algorithm" alg)
(deftheorem example "Example" exmpl)
(deftheorem myquestion "Question" qqq)
(deftheorem assumption "Assumption" assump)
(deftheorem observation "Observation" obsv)

;; With this, org-special-block-extras-mode is not needed.
;; Things will break though if that mode is activated and then deactivated again.
(add-hook 'org-export-before-parsing-functions 'org--support-special-blocks-with-args)

;; Reset special-block-*-labels{-cdr} before export.
(add-hook 'org-export-before-processing-functions
          (lambda (backend)
            (setq special-block-thm-labels '())
            (setq special-block-thm-labels-cdr nil)
            (setq special-block-lem-labels '())
            (setq special-block-lem-labels-cdr nil)
            (setq special-block-dfn-labels '())
            (setq special-block-dfn-labels-cdr nil)
            (setq special-block-prob-labels '())
            (setq special-block-prob-labels-cdr nil)
            (setq special-block-conj-labels '())
            (setq special-block-conj-labels-cdr nil)
            (setq special-block-alg-labels '())
            (setq special-block-alg-labels-cdr nil)
            (setq special-block-exmpl-labels '())
            (setq special-block-exmpl-labels-cdr nil)
            (setq special-block-qqq-labels '())
            (setq special-block-qqq-labels-cdr nil)
            (setq special-block-assump-labels '())
            (setq special-block-assump-labels-cdr nil)
            (setq special-block-obsv-labels '())
            (setq special-block-obsv-labels-cdr nil)
            ))



;;;
;;; Public functions
;;;

(defun build/org-files ()
  "Return all org files under base-dir, excluding emacs/ and submodule/ directories."
  (directory-files-recursively
   (file-name-as-directory base-dir) "\\.org$" nil
   (lambda (x) (and (not (string-match-p "emacs" x))
                    (not (string-match-p "submodule" x))))))

(defun build/export-all ()
  "Export all org-files to Hugo markdown and reveal.js slides."
  (let ((search-path (file-name-as-directory base-dir)))
    (message "[build] Looking for files at %s" search-path)
    (dolist (org-file (build/org-files))
      (with-current-buffer (find-file org-file)
        (message "[build] Exporting (hugo) %s" org-file)
        (org-hugo-export-wim-to-md :all-subtrees nil nil nil)))
    (build/export-slides)
    (message "Done!")))

(defun build/export-slides ()
  "Export org files with #+reveal_export_file_name as reveal.js slides."
  (message "[build] Looking for reveal slides")
  (dolist (org-file (build/org-files))
    (with-temp-buffer
      (insert-file-contents org-file)
      (when (re-search-forward "^[ \t]*#\\+REVEAL_EXPORT_FILE_NAME:" nil t)
        (with-current-buffer (find-file org-file)
          (message "[build] Exporting (reveal) %s" org-file)
          (org-reveal-export-to-html)))))
  (message "Done exporting slides!"))

(provide 'build/export-all)

;;; init.el ends here
