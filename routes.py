import os
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import quote
from app import db
from models import User, Project, Proposal, Milestone, Review, Dispute
from forms import LoginForm, RegistrationForm, ProjectForm, ProposalForm, MilestoneForm, ReviewForm, DisputeForm
from datetime import datetime, timedelta

def register_routes(app):
    
    @app.route('/')
    def index():
        recent_projects = Project.query.filter_by(status='approved').order_by(Project.created_at.desc()).limit(6).all()
        total_projects = Project.query.filter_by(status='approved').count()
        total_experts = User.query.filter_by(role='expert', is_approved=True).count()
        total_students = User.query.filter_by(role='student', is_approved=True).count()
        
        stats = {
            'total_projects': total_projects,
            'total_experts': total_experts,
            'total_students': total_students,
            'active_projects': Project.query.filter_by(status='active').count()
        }
        
        return render_template('index.html', recent_projects=recent_projects, stats=stats)
    
    # Authentication Routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                if not user.is_approved and user.role != 'admin':
                    flash('Your account is pending approval. Please wait for admin approval.', 'warning')
                    return redirect(url_for('login'))
                
                login_user(user)
                flash(f'Welcome back, {user.full_name or user.username}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            flash('Invalid email or password.', 'danger')
        return render_template('auth/login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists. Please choose a different one.', 'danger')
                return render_template('auth/register.html', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please use a different email or login.', 'danger')
                return render_template('auth/register.html', form=form)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                phone=form.phone.data,
                role=form.role.data,
                password_hash=generate_password_hash(form.password.data),
                university=form.university.data if form.role.data == 'student' else None,
                bio=form.bio.data,
                skills=form.skills.data if form.role.data == 'expert' else None,
                is_approved=form.role.data == 'student'  # Auto-approve students, experts need approval
            )
            
            db.session.add(user)
            db.session.commit()
            
            if user.role == 'student':
                flash('Registration successful! You can now login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration successful! Your account is pending admin approval.', 'info')
                return redirect(url_for('login'))
        
        return render_template('auth/register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    # Dashboard Routes
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.role == 'expert':
            return redirect(url_for('expert_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
    
    # Student Routes
    @app.route('/student/dashboard')
    @login_required
    def student_dashboard():
        if current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        projects = Project.query.filter_by(student_id=current_user.id).order_by(Project.created_at.desc()).all()
        return render_template('student/dashboard.html', projects=projects)
    
    @app.route('/student/post-project', methods=['GET', 'POST'])
    @login_required
    def post_project():
        if current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        form = ProjectForm()
        if form.validate_on_submit():
            if form.budget_min.data > form.budget_max.data:
                flash('Minimum budget cannot be greater than maximum budget.', 'danger')
                return render_template('student/post_project.html', form=form)
            
            project = Project(
                title=form.title.data,
                category=form.category.data,
                description=form.description.data,
                requirements=form.requirements.data,
                tech_stack=form.tech_stack.data,
                budget_min=form.budget_min.data,
                budget_max=form.budget_max.data,
                duration_weeks=form.duration_weeks.data,
                student_id=current_user.id,
                deadline=datetime.utcnow() + timedelta(weeks=form.duration_weeks.data)
            )
            
            db.session.add(project)
            db.session.commit()
            flash('Project posted successfully! It will be visible after admin approval.', 'success')
            return redirect(url_for('student_dashboard'))
        
        return render_template('student/post_project.html', form=form)
    
    @app.route('/student/project/<int:project_id>')
    @login_required
    def student_project_detail(project_id):
        project = Project.query.get_or_404(project_id)
        if project.student_id != current_user.id and current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        proposals = Proposal.query.filter_by(project_id=project_id).order_by(Proposal.created_at.desc()).all()
        milestones = Milestone.query.filter_by(project_id=project_id).order_by(Milestone.created_at.asc()).all()
        
        return render_template('student/project_detail.html', project=project, proposals=proposals, milestones=milestones)
    
    @app.route('/student/accept-proposal/<int:proposal_id>')
    @login_required
    def accept_proposal(proposal_id):
        proposal = Proposal.query.get_or_404(proposal_id)
        project = proposal.project
        
        if project.student_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Update proposal status
        proposal.status = 'accepted'
        
        # Update project
        project.status = 'active'
        project.selected_expert_id = proposal.expert_id
        
        # Reject other proposals
        other_proposals = Proposal.query.filter_by(project_id=project.id).filter(Proposal.id != proposal_id).all()
        for other_proposal in other_proposals:
            other_proposal.status = 'rejected'
        
        db.session.commit()
        flash('Proposal accepted! The project is now active.', 'success')
        return redirect(url_for('student_project_detail', project_id=project.id))
    
    # Expert Routes
    @app.route('/expert/dashboard')
    @login_required
    def expert_dashboard():
        if current_user.role != 'expert':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get expert's proposals and active projects
        proposals = Proposal.query.filter_by(expert_id=current_user.id).order_by(Proposal.created_at.desc()).all()
        active_projects = Project.query.filter_by(selected_expert_id=current_user.id, status='active').all()
        
        return render_template('expert/dashboard.html', proposals=proposals, active_projects=active_projects)
    
    @app.route('/expert/browse-projects')
    @login_required
    def browse_projects():
        if current_user.role != 'expert':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Project.query.filter_by(status='approved')
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Project.title.contains(search) | Project.description.contains(search))
        
        projects = query.order_by(Project.created_at.desc()).all()
        
        # Get categories for filter
        categories = [
            ('web_development', 'Web Development'),
            ('mobile_app', 'Mobile Application'),
            ('data_science', 'Data Science & Analytics'),
            ('machine_learning', 'Machine Learning/AI'),
            ('software_engineering', 'Software Engineering'),
            ('database_systems', 'Database Systems'),
            ('cybersecurity', 'Cybersecurity'),
            ('game_development', 'Game Development'),
            ('embedded_systems', 'Embedded Systems'),
            ('blockchain', 'Blockchain'),
            ('other', 'Other')
        ]
        
        return render_template('expert/browse_projects.html', projects=projects, categories=categories, current_category=category, search=search)
    
    @app.route('/expert/submit-proposal/<int:project_id>', methods=['GET', 'POST'])
    @login_required
    def submit_proposal(project_id):
        if current_user.role != 'expert':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        project = Project.query.get_or_404(project_id)
        
        # Check if expert already submitted a proposal
        existing_proposal = Proposal.query.filter_by(project_id=project_id, expert_id=current_user.id).first()
        if existing_proposal:
            flash('You have already submitted a proposal for this project.', 'warning')
            return redirect(url_for('browse_projects'))
        
        form = ProposalForm()
        if form.validate_on_submit():
            if form.proposed_budget.data < project.budget_min or form.proposed_budget.data > project.budget_max:
                flash(f'Proposed budget must be between ${project.budget_min} and ${project.budget_max}.', 'danger')
                return render_template('expert/submit_proposal.html', form=form, project=project)
            
            proposal = Proposal(
                project_id=project_id,
                expert_id=current_user.id,
                cover_letter=form.cover_letter.data,
                proposed_budget=form.proposed_budget.data,
                delivery_time_weeks=form.delivery_time_weeks.data
            )
            
            db.session.add(proposal)
            db.session.commit()
            flash('Proposal submitted successfully!', 'success')
            return redirect(url_for('browse_projects'))
        
        return render_template('expert/submit_proposal.html', form=form, project=project)
    
    # Admin Routes
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        pending_projects = Project.query.filter_by(status='pending').count()
        pending_users = User.query.filter_by(is_approved=False).filter(User.role != 'admin').count()
        total_projects = Project.query.count()
        total_users = User.query.filter(User.role != 'admin').count()
        active_projects = Project.query.filter_by(status='active').count()
        open_disputes = Dispute.query.filter_by(status='open').count()
        
        stats = {
            'pending_projects': pending_projects,
            'pending_users': pending_users,
            'total_projects': total_projects,
            'total_users': total_users,
            'active_projects': active_projects,
            'open_disputes': open_disputes
        }
        
        return render_template('admin/dashboard.html', stats=stats)
    
    @app.route('/admin/manage-projects')
    @login_required
    def manage_projects():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        status_filter = request.args.get('status', 'all')
        
        if status_filter == 'all':
            projects = Project.query.order_by(Project.created_at.desc()).all()
        else:
            projects = Project.query.filter_by(status=status_filter).order_by(Project.created_at.desc()).all()
        
        return render_template('admin/manage_projects.html', projects=projects, status_filter=status_filter)
    
    @app.route('/admin/approve-project/<int:project_id>')
    @login_required
    def approve_project(project_id):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        project = Project.query.get_or_404(project_id)
        project.status = 'approved'
        db.session.commit()
        flash('Project approved successfully!', 'success')
        return redirect(url_for('manage_projects'))
    
    @app.route('/admin/reject-project/<int:project_id>')
    @login_required
    def reject_project(project_id):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        project = Project.query.get_or_404(project_id)
        project.status = 'rejected'
        db.session.commit()
        flash('Project rejected.', 'info')
        return redirect(url_for('manage_projects'))
    
    @app.route('/admin/manage-users')
    @login_required
    def manage_users():
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        role_filter = request.args.get('role', 'all')
        approval_filter = request.args.get('approval', 'all')
        
        query = User.query.filter(User.role != 'admin')
        
        if role_filter != 'all':
            query = query.filter_by(role=role_filter)
        
        if approval_filter == 'pending':
            query = query.filter_by(is_approved=False)
        elif approval_filter == 'approved':
            query = query.filter_by(is_approved=True)
        
        users = query.order_by(User.created_at.desc()).all()
        
        return render_template('admin/manage_users.html', users=users, role_filter=role_filter, approval_filter=approval_filter)
    
    @app.route('/admin/approve-user/<int:user_id>')
    @login_required
    def approve_user(user_id):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        user = User.query.get_or_404(user_id)
        user.is_approved = True
        db.session.commit()
        flash(f'User {user.username} approved successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    # Milestone Routes
    @app.route('/project/<int:project_id>/milestones')
    @login_required
    def project_milestones(project_id):
        project = Project.query.get_or_404(project_id)
        
        # Check access
        if not (project.student_id == current_user.id or 
                project.selected_expert_id == current_user.id or 
                current_user.role == 'admin'):
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        milestones = Milestone.query.filter_by(project_id=project_id).order_by(Milestone.created_at.asc()).all()
        form = MilestoneForm()
        
        return render_template('shared/milestones.html', project=project, milestones=milestones, form=form)
    
    @app.route('/project/<int:project_id>/add-milestone', methods=['POST'])
    @login_required
    def add_milestone(project_id):
        project = Project.query.get_or_404(project_id)
        
        # Only student can add milestones
        if project.student_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        form = MilestoneForm()
        if form.validate_on_submit():
            milestone = Milestone(
                project_id=project_id,
                title=form.title.data,
                description=form.description.data,
                budget_percentage=form.budget_percentage.data
            )
            
            db.session.add(milestone)
            db.session.commit()
            flash('Milestone added successfully!', 'success')
        
        return redirect(url_for('project_milestones', project_id=project_id))
    
    @app.route('/milestone/<int:milestone_id>/submit')
    @login_required
    def submit_milestone(milestone_id):
        milestone = Milestone.query.get_or_404(milestone_id)
        project = milestone.project
        
        # Only assigned expert can submit milestones
        if project.selected_expert_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        milestone.status = 'submitted'
        milestone.submitted_at = datetime.utcnow()
        db.session.commit()
        flash('Milestone submitted for review!', 'success')
        return redirect(url_for('project_milestones', project_id=project.id))
    
    @app.route('/milestone/<int:milestone_id>/approve')
    @login_required
    def approve_milestone(milestone_id):
        milestone = Milestone.query.get_or_404(milestone_id)
        project = milestone.project
        
        # Only student can approve milestones
        if project.student_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        milestone.status = 'approved'
        milestone.approved_at = datetime.utcnow()
        db.session.commit()
        flash('Milestone approved!', 'success')
        return redirect(url_for('project_milestones', project_id=project.id))
    
    # WhatsApp Integration
    @app.route('/chat/<int:user_id>')
    @login_required
    def whatsapp_chat(user_id):
        user = User.query.get_or_404(user_id)
        
        if not user.phone:
            flash('User has not provided a phone number.', 'warning')
            return redirect(request.referrer or url_for('dashboard'))
        
        # Clean phone number (remove non-digits)
        phone = ''.join(filter(str.isdigit, user.phone))
        
        # Create WhatsApp message
        message = f"Hi {user.full_name or user.username}, I'm contacting you regarding a project on FYP Marketplace."
        encoded_message = quote(message)
        
        whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
        
        return redirect(whatsapp_url)
    
    # Review System
    @app.route('/project/<int:project_id>/review/<int:reviewee_id>', methods=['GET', 'POST'])
    @login_required
    def submit_review(project_id, reviewee_id):
        project = Project.query.get_or_404(project_id)
        reviewee = User.query.get_or_404(reviewee_id)
        
        # Check if user can review
        if not (project.student_id == current_user.id or project.selected_expert_id == current_user.id):
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Check if already reviewed
        existing_review = Review.query.filter_by(
            project_id=project_id,
            reviewer_id=current_user.id,
            reviewee_id=reviewee_id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this person for this project.', 'warning')
            return redirect(url_for('dashboard'))
        
        form = ReviewForm()
        if form.validate_on_submit():
            review = Review(
                project_id=project_id,
                reviewer_id=current_user.id,
                reviewee_id=reviewee_id,
                rating=int(form.rating.data),
                comment=form.comment.data
            )
            
            db.session.add(review)
            
            # Update user rating
            user_reviews = Review.query.filter_by(reviewee_id=reviewee_id).all()
            if user_reviews:
                total_rating = sum([r.rating for r in user_reviews]) + int(form.rating.data)
                total_count = len(user_reviews) + 1
                reviewee.rating = total_rating / total_count
                reviewee.total_reviews = total_count
            else:
                reviewee.rating = int(form.rating.data)
                reviewee.total_reviews = 1
            
            db.session.commit()
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('shared/review_form.html', form=form, project=project, reviewee=reviewee)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
